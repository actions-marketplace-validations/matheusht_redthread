"""Stage node functions for the RedThread supervisor graph."""

from __future__ import annotations

import logging
from typing import Any

from redthread.config.settings import RedThreadSettings
from redthread.models import CampaignConfig
from redthread.orchestration.agentic_security_runtime import run_agentic_security_review
from redthread.orchestration.supervisor_state import SupervisorState

logger = logging.getLogger(__name__)


async def generate_personas_node(state: SupervisorState) -> dict[str, Any]:
    """Generate adversarial personas for the campaign objective."""
    from redthread.personas.adaptive_weighting import AdaptivePersonaWeightingPlan
    from redthread.personas.generator import PersonaGenerator
    from redthread.personas.prompt_layers import PromptingLayerProfile

    settings = RedThreadSettings.model_validate(state["settings_dict"])
    config = CampaignConfig.model_validate(state["config_dict"])
    gen = PersonaGenerator(settings)
    prompting_layer_profile = (
        PromptingLayerProfile.model_validate(config.prompting_layer_profile)
        if config.prompting_layer_profile else None
    )
    weighting_plan = (
        AdaptivePersonaWeightingPlan.model_validate(config.persona_weighting_plan)
        if config.persona_weighting_plan else None
    )
    personas = await gen.generate_batch(
        objective=config.objective,
        count=config.num_personas,
        prompting_layer_profile=prompting_layer_profile,
        persona_weighting_plan=weighting_plan,
    )
    return {"persona_dicts": [p.model_dump(mode="json") for p in personas]}


def worker_canary_update(
    outputs: list[dict[str, Any]],
    existing_report: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Merge live canary reports emitted by workers."""
    from redthread.orchestration.runtime_summary import merge_canary_reports

    reports = [existing_report] if existing_report else []
    reports.extend(
        output["live_canary_report"]
        for output in outputs
        if isinstance(output.get("live_canary_report"), dict)
    )
    merged = merge_canary_reports(reports)
    if not merged:
        return {}
    return {
        "live_canary_report": merged,
        "live_canary_event_total": merged.get("stage_count", 0),
    }


async def collect_results_node(state: SupervisorState) -> dict[str, Any]:
    """Collect all attack worker outputs."""
    errors = [r.get("error") for r in state["attack_results"] if r.get("error")]
    failures = sum(
        1 for r in state["attack_results"] if r.get("error") or not r.get("result_dict")
    )
    return {
        "errors": errors,
        "attack_worker_total": len(state["attack_results"]),
        "attack_worker_failures": failures,
        **worker_canary_update(state["attack_results"]),
    }


async def judge_all_results_node(state: SupervisorState) -> dict[str, Any]:
    """Run JudgeAgent re-evaluation on collected attack results sequentially."""
    from redthread.orchestration.graphs.judge_graph import run_judge_worker

    judged: list[dict[str, Any]] = []
    errors: list[str] = []
    failures = 0
    config = state["config_dict"]
    judge_inputs = [r for r in state["attack_results"] if r.get("result_dict")]
    for raw_result in judge_inputs:
        output = await run_judge_worker({
            "settings_dict": state["settings_dict"],
            "result_dict": raw_result["result_dict"],
            "rubric_name": config.get("rubric_name", "authorization_bypass"),
            "judged_result_dict": None,
            "is_jailbreak": False,
            "final_score": 0.0,
            "error": None,
        })
        if output.get("judged_result_dict"):
            judged.append(output["judged_result_dict"])
        if output.get("error"):
            errors.append(output["error"])
            failures += 1
    return {
        "judged_results": judged,
        "errors": errors,
        "judge_worker_total": len(judge_inputs),
        "judge_worker_failures": failures,
        **worker_canary_update(judged, state.get("live_canary_report")),
    }


async def analyze_agentic_security_node(state: SupervisorState) -> dict[str, Any]:
    """Run additive agentic-security runtime review."""
    report = run_agentic_security_review(CampaignConfig.model_validate(state["config_dict"]))
    return {
        "agentic_security_report": report,
        "agentic_action_total": report.get("action_total", 0),
        "authorization_decision_counts": report.get("authorization_decision_counts", {}),
        "canary_event_total": report.get("canary_event_total", 0),
        "canary_report": report.get("canary_report", {}),
        "amplification_metrics": report.get("amplification_metrics", {}),
        "budget_stop_triggered": report.get("budget_stop_triggered", False),
        "untrusted_lineage_action_total": report.get("untrusted_lineage_action_total", 0),
    }


async def defense_synthesis_node(state: SupervisorState) -> dict[str, Any]:
    """Run DefenseWorker for all confirmed jailbreaks."""
    from redthread.core.defense_status import (
        candidate_flags,
        validated_candidate,
        validated_candidate_count_fields,
    )
    from redthread.orchestration.graphs.defense_graph import run_defense_worker

    records: list[dict[str, Any]] = []
    errors: list[str] = []
    failures = 0
    indexed_candidates = 0
    defense_inputs = [
        result for result in state["judged_results"]
        if result.get("verdict", {}).get("is_jailbreak")
    ]
    for result_dict in defense_inputs:
        output = await run_defense_worker({
            "settings_dict": state["settings_dict"],
            "result_dict": result_dict,
            **candidate_flags(False),
            "guardrail_clause": None,
            "error": None,
        })
        validated = validated_candidate(output)
        record = {
            **candidate_flags(validated),
            "guardrail_clause": output.get("guardrail_clause"),
        }
        record.update(output.get("record_dict") or {})
        records.append(record)
        if validated:
            indexed_candidates += 1
        if output.get("error"):
            errors.append(output["error"])
            failures += 1
    return {
        "defense_records": records,
        "errors": errors,
        "defense_worker_total": len(defense_inputs),
        "defense_worker_failures": failures,
        **validated_candidate_count_fields(indexed_candidates),
        **worker_canary_update(records, state.get("live_canary_report")),
    }


_worker_canary_update = worker_canary_update

__all__ = [
    "_worker_canary_update",
    "analyze_agentic_security_node",
    "collect_results_node",
    "defense_synthesis_node",
    "generate_personas_node",
    "judge_all_results_node",
    "worker_canary_update",
]
