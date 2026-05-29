"""Compatibility exports for the shared PyRIT adapter boundary."""

from redthread.pyrit_adapters.capabilities import (
    CapabilityCheck,
    CapabilityRequirement,
    RedThreadTargetCapabilities,
    UnsupportedTargetCapabilityError,
    check_requirement,
    from_pyrit_target,
)
from redthread.pyrit_adapters.client import RedThreadTarget
from redthread.pyrit_adapters.execution_records import (
    ExecutionMetadata,
    ExecutionRecord,
    ExecutionRecorder,
    build_execution_record,
)
from redthread.pyrit_adapters.factories import (
    build_attacker,
    build_defense_architect,
    build_judge_llm,
    build_rollout_attacker,
    build_target,
)
from redthread.pyrit_adapters.runtime import _build_pyrit_target, ensure_pyrit_memory_initialized
from redthread.pyrit_adapters.send_helpers import (
    send_with_execution_metadata,
    send_with_usage_and_execution_metadata,
)

__all__ = [
    "CapabilityCheck",
    "CapabilityRequirement",
    "ExecutionMetadata",
    "ExecutionRecord",
    "ExecutionRecorder",
    "RedThreadTarget",
    "RedThreadTargetCapabilities",
    "UnsupportedTargetCapabilityError",
    "build_attacker",
    "build_defense_architect",
    "build_execution_record",
    "build_judge_llm",
    "build_rollout_attacker",
    "build_target",
    "check_requirement",
    "ensure_pyrit_memory_initialized",
    "from_pyrit_target",
    "send_with_execution_metadata",
    "send_with_usage_and_execution_metadata",
    "_build_pyrit_target",
]
