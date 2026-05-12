"""Native importer for adopt-redthread sanitized intent evidence packages."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from redthread.reporting.external_evidence import (
    ExternalEvidenceBundle,
    ExternalEvidenceItem,
    ExternalEvidenceSource,
    _probe_seed,
)
from redthread.reporting.public_artifacts import prompt_safe_json

ADOPT_REDTHREAD_INTENT_EVIDENCE_SCHEMA = "redthread.intent_evidence.v1"
ADOPT_REDTHREAD_PENTEST_CONTEXT_SCHEMA = "adopt_redthread.pentest_context_package.v0"


def import_adopt_redthread_intent_evidence_file(
    input_path: Path,
    *,
    output_path: Path,
) -> ExternalEvidenceBundle:
    """Import an adopt-redthread intent evidence package as weak RedThread evidence."""
    bundle = adopt_redthread_evidence_from_payload(_read_json(input_path))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(prompt_safe_json(bundle.model_dump(mode="json")), encoding="utf-8")
    return bundle


def adopt_redthread_evidence_from_payload(payload: object) -> ExternalEvidenceBundle:
    """Convert supported adopt-redthread packages into RedThread weak external evidence."""
    if not isinstance(payload, Mapping):
        msg = "adopt-redthread input must be a JSON object"
        raise ValueError(msg)
    schema = payload.get("schema_version")
    if schema == ADOPT_REDTHREAD_INTENT_EVIDENCE_SCHEMA:
        return adopt_redthread_intent_evidence_from_payload(payload)
    if schema == ADOPT_REDTHREAD_PENTEST_CONTEXT_SCHEMA:
        return adopt_redthread_pentest_context_from_payload(payload)
    msg = "unsupported adopt-redthread evidence schema"
    raise ValueError(msg)


def adopt_redthread_intent_evidence_from_payload(payload: object) -> ExternalEvidenceBundle:
    """Convert redthread.intent_evidence.v1 into RedThread weak external evidence."""
    if not isinstance(payload, Mapping):
        msg = "adopt-redthread intent evidence input must be a JSON object"
        raise ValueError(msg)
    package = dict(payload)
    _validate_package_boundary(package)

    items: list[ExternalEvidenceItem] = []
    for evidence in package.get("evidence", []):
        if not isinstance(evidence, Mapping):
            msg = "adopt-redthread evidence entries must be JSON objects"
            raise ValueError(msg)
        items.append(_evidence_item(dict(evidence), package))
    for step in package.get("attack_plan", {}).get("steps", []):
        if not isinstance(step, Mapping):
            msg = "adopt-redthread attack-plan steps must be JSON objects"
            raise ValueError(msg)
        items.append(_attack_step_item(dict(step), package))
    if not items:
        msg = "adopt-redthread intent evidence must include evidence or attack-plan steps"
        raise ValueError(msg)
    return ExternalEvidenceBundle(
        source=ExternalEvidenceSource.ADOPT_REDTHREAD,
        items=items,
        limitations=[
            "Imported adopt-redthread intent evidence is weak imported context, not proof.",
            "JudgeAgent confirmation is required before creating findings or regression cases.",
            "No raw HAR, URL, header, cookie, body, payload, or secret is imported.",
        ],
    )


def adopt_redthread_pentest_context_from_payload(payload: object) -> ExternalEvidenceBundle:
    """Convert adopt_redthread.pentest_context_package.v0 into weak RedThread evidence."""
    if not isinstance(payload, Mapping):
        msg = "adopt-redthread pentest context input must be a JSON object"
        raise ValueError(msg)
    package = dict(payload)
    _validate_pentest_context_boundary(package)
    items: list[ExternalEvidenceItem] = []
    for hypothesis in package.get("attack_surface_hypotheses", []):
        if not isinstance(hypothesis, Mapping):
            msg = "adopt-redthread pentest hypotheses must be JSON objects"
            raise ValueError(msg)
        item = _pentest_hypothesis_item(dict(hypothesis), package)
        items.append(item)
    if not items:
        msg = "adopt-redthread pentest context package must include hypotheses"
        raise ValueError(msg)
    return ExternalEvidenceBundle(
        source=ExternalEvidenceSource.ADOPT_REDTHREAD,
        items=items,
        limitations=[
            "Imported adopt-redthread pentest context is weak planning context, not proof.",
            "Opt-in auth/write bundles are required before authenticated or state-changing execution.",
            "JudgeAgent confirmation is required before creating findings or regression cases.",
            "No raw HAR, URL, header, cookie, body, auth value, or secret is imported.",
        ],
    )


def _validate_package_boundary(package: dict[str, Any]) -> None:
    if package.get("schema_version") != ADOPT_REDTHREAD_INTENT_EVIDENCE_SCHEMA:
        msg = "unsupported adopt-redthread intent evidence schema"
        raise ValueError(msg)
    source = package.get("source", {})
    privacy = package.get("privacy", {})
    intent = package.get("intent", {})
    redthread_import = package.get("redthread_import", {})
    if source.get("raw_artifacts_included") is not False:
        msg = "adopt-redthread package must not include raw artifacts"
        raise ValueError(msg)
    if not privacy.get("sanitized"):
        msg = "adopt-redthread package must be sanitized"
        raise ValueError(msg)
    forbidden_privacy_flags = (
        "raw_har_included",
        "raw_urls_included",
        "headers_included",
        "raw_headers_included",
        "cookies_included",
        "raw_cookies_included",
        "bodies_included",
        "raw_bodies_included",
        "raw_payloads_included",
        "secrets_included",
    )
    if any(flag in privacy and privacy.get(flag) is not False for flag in forbidden_privacy_flags):
        msg = "adopt-redthread package includes forbidden raw/privacy flags"
        raise ValueError(msg)
    if intent.get("not_a_finding") is not True:
        msg = "adopt-redthread package must declare not_a_finding"
        raise ValueError(msg)
    if redthread_import.get("requires_human_review") is not True:
        msg = "adopt-redthread package must require human review"
        raise ValueError(msg)
    if redthread_import.get("judge_agent_required") is not True:
        msg = "adopt-redthread package must require JudgeAgent"
        raise ValueError(msg)
    if redthread_import.get("eligible_for_regression") is not False:
        msg = "adopt-redthread package cannot be regression eligible on import"
        raise ValueError(msg)


def _validate_pentest_context_boundary(package: dict[str, Any]) -> None:
    if package.get("schema_version") != ADOPT_REDTHREAD_PENTEST_CONTEXT_SCHEMA:
        msg = "unsupported adopt-redthread pentest context schema"
        raise ValueError(msg)
    source = package.get("source", {})
    privacy = package.get("privacy", {})
    safety = package.get("safety_policy", {})
    if source.get("raw_artifacts_included") is not False:
        msg = "adopt-redthread pentest context must not include raw artifacts"
        raise ValueError(msg)
    if not privacy.get("sanitized"):
        msg = "adopt-redthread pentest context must be sanitized"
        raise ValueError(msg)
    forbidden_flags = (
        "raw_har_included",
        "raw_urls_included",
        "raw_headers_included",
        "raw_cookies_included",
        "raw_bodies_included",
        "raw_ids_included",
        "auth_values_included",
        "secrets_included",
    )
    if any(privacy.get(flag) is not False for flag in forbidden_flags):
        msg = "adopt-redthread pentest context includes forbidden raw/privacy flags"
        raise ValueError(msg)
    if safety.get("default_live_execution_allowed") is not False:
        msg = "adopt-redthread pentest context cannot authorize live execution"
        raise ValueError(msg)
    if safety.get("judge_agent_required") is not True:
        msg = "adopt-redthread pentest context must require JudgeAgent"
        raise ValueError(msg)
    for hypothesis in package.get("attack_surface_hypotheses", []):
        if not isinstance(hypothesis, Mapping):
            continue
        if hypothesis.get("not_a_finding") is not True:
            msg = "adopt-redthread pentest context hypotheses must be not_a_finding"
            raise ValueError(msg)
        if hypothesis.get("requires_judge_confirmation") is not True:
            msg = "adopt-redthread pentest context hypotheses must require JudgeAgent"
            raise ValueError(msg)
        if not hypothesis.get("evidence_ids"):
            msg = "adopt-redthread pentest context hypotheses must cite evidence"
            raise ValueError(msg)


def _evidence_item(evidence: dict[str, Any], package: dict[str, Any]) -> ExternalEvidenceItem:
    source_id = str(evidence.get("id") or evidence.get("source_observation_id") or "adopt-evidence")
    return ExternalEvidenceItem(
        source=ExternalEvidenceSource.ADOPT_REDTHREAD,
        source_id=source_id,
        title=f"adopt-redthread sanitized evidence {source_id}",
        description=str(evidence.get("summary", "")),
        detector_hint_context={
            "adopt_redthread_schema": package.get("schema_version"),
            "source_observation_id": evidence.get("source_observation_id"),
            "limitations": evidence.get("limitations", []),
            "strength": evidence.get("strength"),
        },
    )


def _pentest_hypothesis_item(hypothesis: dict[str, Any], package: dict[str, Any]) -> ExternalEvidenceItem:
    source_id = str(hypothesis.get("hypothesis_id") or "adopt-pentest-hypothesis")
    summary = str(hypothesis.get("summary", ""))
    return ExternalEvidenceItem(
        source=ExternalEvidenceSource.ADOPT_REDTHREAD,
        source_id=source_id,
        title=f"adopt-redthread pentest context {source_id}",
        description=summary,
        detector_hint_context={
            "adopt_redthread_schema": package.get("schema_version"),
            "category": hypothesis.get("category"),
            "subject_id": hypothesis.get("subject_id"),
            "evidence_ids": hypothesis.get("evidence_ids", []),
            "missing_context": hypothesis.get("missing_context", []),
            "requires_judge_confirmation": hypothesis.get("requires_judge_confirmation"),
            "not_a_finding": hypothesis.get("not_a_finding"),
            "auth_bundle_required_before_execution": True,
        },
        candidate_probe_seed=_probe_seed(source_id, summary, hypothesis) if summary else None,
    )


def _attack_step_item(step: dict[str, Any], package: dict[str, Any]) -> ExternalEvidenceItem:
    if step.get("requires_raw_payload") is not False:
        msg = "adopt-redthread attack steps cannot require raw payloads"
        raise ValueError(msg)
    if step.get("requires_live_execution") is not False:
        msg = "adopt-redthread attack steps cannot require live execution"
        raise ValueError(msg)
    source_id = str(step.get("id") or "adopt-step")
    action = str(step.get("action", ""))
    return ExternalEvidenceItem(
        source=ExternalEvidenceSource.ADOPT_REDTHREAD,
        source_id=source_id,
        title=f"adopt-redthread candidate step {source_id}",
        description=action,
        detector_hint_context={
            "adopt_redthread_schema": package.get("schema_version"),
            "expected_signal": step.get("expected_signal"),
            "success_condition": step.get("success_condition"),
            "supporting_evidence_ids": step.get("supporting_evidence_ids", []),
            "requires_raw_payload": step.get("requires_raw_payload"),
            "requires_live_execution": step.get("requires_live_execution"),
        },
        candidate_probe_seed=_probe_seed(source_id, action, step) if action else None,
    )


def _read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


__all__ = [
    "ADOPT_REDTHREAD_INTENT_EVIDENCE_SCHEMA",
    "ADOPT_REDTHREAD_PENTEST_CONTEXT_SCHEMA",
    "adopt_redthread_evidence_from_payload",
    "adopt_redthread_intent_evidence_from_payload",
    "adopt_redthread_pentest_context_from_payload",
    "import_adopt_redthread_intent_evidence_file",
]
