"""Pareto frontier selection over GEPA candidates (Phase 2).

This replaces the autoresearch anti-pattern of collapsing every candidate to a
single ``max(composite_score)`` winner, which discards specialist variants. GEPA's
thesis (arXiv 2507.19457) is that keeping per-objective scores and selecting from a
Pareto frontier preserves the specialists later mutations and merges depend on.

A candidate is represented here by its per-objective score vector (one axis per
objective slug). The frontier is the set of candidates not dominated on every axis.
Parent selection samples the frontier weighted by how many objectives each candidate
*leads*, exactly as the paper describes.

Pure, dependency-free, deterministic given a seeded RNG — testable without any live
call, identical in spirit to the Phase 0 shadow harness.
"""

from __future__ import annotations

import random
from collections.abc import Sequence

from pydantic import BaseModel, Field

from redthread.research.gepa_candidate import GepaEvaluationResult, GepaSplit


class ParetoCandidate(BaseModel):
    """A candidate reduced to its per-objective score vector for frontier ranking."""

    candidate_id: str
    scores: dict[str, float] = Field(default_factory=dict)


def candidate_from_result(
    result: GepaEvaluationResult,
    *,
    split: GepaSplit = GepaSplit.TRAIN,
) -> ParetoCandidate:
    """Project a scored candidate onto its per-objective vector for one split.

    The control split is never used as a Pareto axis — it is a gate, not an
    objective. If multiple entries share a slug, the max is taken.
    """
    scores: dict[str, float] = {}
    for item in result.objective_scores:
        if item.split is not split:
            continue
        scores[item.slug] = max(scores.get(item.slug, item.objective_score), item.objective_score)
    return ParetoCandidate(candidate_id=result.candidate_id, scores=scores)


def dominates(a: ParetoCandidate, b: ParetoCandidate) -> bool:
    """Return True if ``a`` Pareto-dominates ``b``.

    Domination requires ``a`` to be no worse on every shared objective and strictly
    better on at least one. Missing axes are treated as 0.0.
    """
    slugs = set(a.scores) | set(b.scores)
    if not slugs:
        return False
    strictly_better = False
    for slug in slugs:
        av = a.scores.get(slug, 0.0)
        bv = b.scores.get(slug, 0.0)
        if av < bv:
            return False
        if av > bv:
            strictly_better = True
    return strictly_better


def pareto_frontier(candidates: Sequence[ParetoCandidate]) -> list[ParetoCandidate]:
    """Return the non-dominated set, preserving input order.

    A candidate dominated by any other is excluded. Ties (mutually non-dominating)
    are all kept — that is the point: specialists on different objectives survive.
    """
    frontier: list[ParetoCandidate] = []
    for candidate in candidates:
        if any(dominates(other, candidate) for other in candidates if other is not candidate):
            continue
        frontier.append(candidate)
    return frontier


def objective_leaders(frontier: Sequence[ParetoCandidate]) -> dict[str, list[str]]:
    """Map each objective slug to the candidate ids that achieve its max score."""
    leaders: dict[str, list[str]] = {}
    all_slugs = {slug for c in frontier for slug in c.scores}
    for slug in all_slugs:
        best = max((c.scores.get(slug, 0.0) for c in frontier), default=0.0)
        leaders[slug] = [c.candidate_id for c in frontier if c.scores.get(slug, 0.0) == best]
    return leaders


def selection_weights(frontier: Sequence[ParetoCandidate]) -> dict[str, float]:
    """Weight each frontier candidate by how many objectives it leads.

    Mirrors GEPA's stochastic Pareto sampling: specialists that lead more objectives
    are more likely to be selected as parents. Every frontier member gets a floor
    weight of 1 so non-leaders can still be explored.
    """
    leaders = objective_leaders(frontier)
    weights = {c.candidate_id: 1.0 for c in frontier}
    for ids in leaders.values():
        share = 1.0 / len(ids)
        for candidate_id in ids:
            weights[candidate_id] += share
    return weights


def select_parent(
    frontier: Sequence[ParetoCandidate],
    *,
    rng: random.Random,
) -> ParetoCandidate:
    """Sample one parent from the frontier, weighted by objectives led."""
    if not frontier:
        raise ValueError("cannot select a parent from an empty Pareto frontier")
    weights = selection_weights(frontier)
    population = list(frontier)
    chosen = rng.choices(population, weights=[weights[c.candidate_id] for c in population], k=1)
    return chosen[0]
