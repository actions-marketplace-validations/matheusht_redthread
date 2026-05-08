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


def import_adopt_redthread_intent_evidence_file(
    input_path: Path,
    *,
    output_path: Path,
) -> ExternalEvidenceBundle:
    """Import an adopt-redthread intent evidence package as weak RedThread evidence."""
    bundle = adopt_redthread_intent_evidence_from_payload(_read_json(input_path))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(prompt_safe_json(bundle.model_dump(mode="json")), encoding="utf-8")
    return bundle


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
    "adopt_redthread_intent_evidence_from_payload",
    "import_adopt_redthread_intent_evidence_file",
]
