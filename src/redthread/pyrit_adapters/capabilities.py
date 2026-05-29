from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

_TEXT_MODALITY = frozenset({"text"})
_TEXT_MODALITIES = frozenset({_TEXT_MODALITY})


@dataclass(frozen=True)
class RedThreadTargetCapabilities:
    """Stable RedThread view of target capabilities."""

    supports_multi_turn: bool = False
    supports_multi_message_pieces: bool = False
    supports_json_output: bool = False
    supports_json_schema: bool = False
    supports_editable_history: bool = False
    input_modalities: frozenset[frozenset[str]] = _TEXT_MODALITIES
    output_modalities: frozenset[frozenset[str]] = _TEXT_MODALITIES

    def as_metadata(self) -> dict[str, object]:
        return {
            "supports_multi_turn": self.supports_multi_turn,
            "supports_multi_message_pieces": self.supports_multi_message_pieces,
            "supports_json_output": self.supports_json_output,
            "supports_json_schema": self.supports_json_schema,
            "supports_editable_history": self.supports_editable_history,
            "input_modalities": _serialize_modalities(self.input_modalities),
            "output_modalities": _serialize_modalities(self.output_modalities),
        }


@dataclass(frozen=True)
class CapabilityRequirement:
    """Behavior a caller is about to require from a target."""

    requires_multi_turn: bool = False
    requires_multi_message_pieces: bool = False
    requires_json_output: bool = False
    requires_json_schema: bool = False
    requires_editable_history: bool = False
    input_modalities: frozenset[str] = field(default_factory=lambda: _TEXT_MODALITY)
    output_modalities: frozenset[str] = field(default_factory=lambda: _TEXT_MODALITY)

    def as_metadata(self) -> dict[str, object]:
        return {
            "requires_multi_turn": self.requires_multi_turn,
            "requires_multi_message_pieces": self.requires_multi_message_pieces,
            "requires_json_output": self.requires_json_output,
            "requires_json_schema": self.requires_json_schema,
            "requires_editable_history": self.requires_editable_history,
            "input_modalities": sorted(self.input_modalities),
            "output_modalities": sorted(self.output_modalities),
        }


@dataclass(frozen=True)
class CapabilityCheck:
    supported: bool
    reason: str
    missing: tuple[str, ...] = ()

    def as_metadata(self) -> dict[str, object]:
        return {
            "supported": self.supported,
            "reason": self.reason,
            "missing": list(self.missing),
        }


class UnsupportedTargetCapabilityError(RuntimeError):
    """Raised before a provider call when a target cannot meet a requirement."""


def from_pyrit_target(target: Any) -> RedThreadTargetCapabilities:
    """Map a PyRIT 0.12 target into RedThread's stable capability contract."""
    capabilities = getattr(target, "capabilities", None)
    if capabilities is None:
        return RedThreadTargetCapabilities()

    return RedThreadTargetCapabilities(
        supports_multi_turn=bool(getattr(capabilities, "supports_multi_turn", False)),
        supports_multi_message_pieces=bool(
            getattr(capabilities, "supports_multi_message_pieces", False)
        ),
        supports_json_output=bool(getattr(capabilities, "supports_json_output", False)),
        supports_json_schema=bool(getattr(capabilities, "supports_json_schema", False)),
        supports_editable_history=bool(getattr(capabilities, "supports_editable_history", False)),
        input_modalities=_normalize_modalities(getattr(capabilities, "input_modalities", None)),
        output_modalities=_normalize_modalities(getattr(capabilities, "output_modalities", None)),
    )


def check_requirement(
    capabilities: RedThreadTargetCapabilities,
    requirement: CapabilityRequirement | None = None,
) -> CapabilityCheck:
    requirement = requirement or CapabilityRequirement()
    missing: list[str] = []

    if requirement.requires_multi_turn and not capabilities.supports_multi_turn:
        missing.append("multi_turn")
    if requirement.requires_multi_message_pieces and not capabilities.supports_multi_message_pieces:
        missing.append("multi_message_pieces")
    if requirement.requires_json_output and not capabilities.supports_json_output:
        missing.append("json_output")
    if requirement.requires_json_schema and not capabilities.supports_json_schema:
        missing.append("json_schema")
    if requirement.requires_editable_history and not capabilities.supports_editable_history:
        missing.append("editable_history")
    if not _supports_modality_set(capabilities.input_modalities, requirement.input_modalities):
        missing.append("input_modalities")
    if not _supports_modality_set(capabilities.output_modalities, requirement.output_modalities):
        missing.append("output_modalities")

    if missing:
        return CapabilityCheck(
            supported=False,
            reason="target does not support required capability: " + ", ".join(missing),
            missing=tuple(missing),
        )
    return CapabilityCheck(supported=True, reason="target supports required capabilities")


def require_capabilities(
    target: Any,
    requirement: CapabilityRequirement | None = None,
) -> tuple[RedThreadTargetCapabilities, CapabilityCheck]:
    capabilities = from_pyrit_target(target)
    check = check_requirement(capabilities, requirement)
    if not check.supported:
        raise UnsupportedTargetCapabilityError(check.reason)
    return capabilities, check


def _normalize_modalities(value: object) -> frozenset[frozenset[str]]:
    if value is None:
        return _TEXT_MODALITIES
    normalized: set[frozenset[str]] = set()
    for combo in value:  # type: ignore[union-attr]
        if isinstance(combo, str):
            normalized.add(frozenset({combo}))
        else:
            normalized.add(frozenset(str(item) for item in combo))
    return frozenset(normalized) or _TEXT_MODALITIES


def _supports_modality_set(
    supported: frozenset[frozenset[str]],
    required: frozenset[str],
) -> bool:
    return any(required.issubset(combo) for combo in supported)


def _serialize_modalities(value: frozenset[frozenset[str]]) -> list[list[str]]:
    return [sorted(combo) for combo in sorted(value, key=lambda combo: sorted(combo))]
