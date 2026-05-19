"""Smoke tests for TAP attack behavior."""

from __future__ import annotations

import pytest

from redthread.config.settings import AlgorithmType, RedThreadSettings, TargetBackend
from redthread.core.tap import TAPAttack
from redthread.models import AttackOutcome, MitreAtlasTactic, Persona, PsychologicalTrigger


def make_tap_settings(*, depth: int = 2, branching: int = 2, width: int = 3) -> RedThreadSettings:
    return RedThreadSettings(
        target_backend=TargetBackend.OLLAMA,
        target_model="llama3.2:3b",
        attacker_backend=TargetBackend.OLLAMA,
        attacker_model="llama3.2:3b",
        judge_backend=TargetBackend.OPENAI,
        judge_model="gpt-4o",
        openai_api_key="test-key",
        algorithm=AlgorithmType.TAP,
        dry_run=True,
        tree_depth=depth,
        branching_factor=branching,
        tree_width=width,
    )


def make_persona() -> Persona:
    return Persona(
        name="Audit Persona",
        tactic=MitreAtlasTactic.INITIAL_ACCESS,
        technique="AML.T0051",
        cover_story="Routine access review",
        hidden_objective="Check authorization behavior",
        system_prompt="You are conducting a safe authorization review.",
        psychological_triggers=[PsychologicalTrigger.AUTHORITY],
    )


@pytest.mark.asyncio
async def test_tap_dry_run_returns_safe_skipped_result_shape() -> None:
    result = await TAPAttack(make_tap_settings()).run(
        persona=make_persona(),
        target_system_prompt="You are a guarded support assistant.",
        rubric_name="authorization_bypass",
    )

    assert result.trace.algorithm == "tap"
    assert result.trace.outcome == AttackOutcome.SKIPPED
    assert result.verdict.is_jailbreak is False
    assert result.trace.metadata["target_system_prompt"] == "You are a guarded support assistant."


@pytest.mark.asyncio
async def test_tap_dry_run_honors_depth_branching_and_width() -> None:
    result = await TAPAttack(make_tap_settings(depth=3, branching=3, width=2)).run(
        persona=make_persona(),
        target_system_prompt="Guarded prompt.",
        rubric_name="authorization_bypass",
    )

    nodes_by_depth = {}
    for node in result.trace.nodes:
        nodes_by_depth.setdefault(node.depth, []).append(node)

    assert len(nodes_by_depth[0]) == 1
    assert len(nodes_by_depth[1]) == 3
    assert len(nodes_by_depth[2]) == 6
    assert len(nodes_by_depth[3]) == 6
    assert all(
        len([node for node in nodes if not node.is_pruned]) <= 2
        for depth, nodes in nodes_by_depth.items()
        if depth > 0
    )
    assert result.iterations_used == 15
