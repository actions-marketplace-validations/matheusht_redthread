from __future__ import annotations

from dataclasses import dataclass

import pytest
from pyrit.prompt_target.common.target_capabilities import TargetCapabilities

from redthread.pyrit_adapters.capabilities import (
    CapabilityRequirement,
    UnsupportedTargetCapabilityError,
    check_requirement,
    from_pyrit_target,
)
from redthread.pyrit_adapters.client import RedThreadTarget
from redthread.pyrit_adapters.execution_records import ExecutionMetadata


@dataclass
class FakeMessagePiece:
    role: str = "assistant"
    original_value: str = ""
    conversation_id: str = ""
    converted_value: str | None = None


@dataclass
class FakeMessage:
    message_pieces: list[FakeMessagePiece]


class FakePyritTarget:
    def __init__(self, capabilities: TargetCapabilities | None = None) -> None:
        if capabilities is not None:
            self.capabilities = capabilities
        self.calls = 0

    async def send_prompt_async(self, message: FakeMessage) -> list[FakeMessage]:
        self.calls += 1
        return [FakeMessage([FakeMessagePiece(original_value="ok", converted_value="ok")])]


def test_maps_pyrit_012_target_capabilities() -> None:
    target = FakePyritTarget(
        TargetCapabilities(
            supports_multi_turn=True,
            supports_multi_message_pieces=True,
            supports_json_output=True,
            supports_json_schema=True,
            input_modalities=frozenset({frozenset({"text", "image_path"})}),
            output_modalities=frozenset({frozenset({"text"})}),
        )
    )

    capabilities = from_pyrit_target(target)

    assert capabilities.supports_multi_turn is True
    assert capabilities.supports_multi_message_pieces is True
    assert capabilities.supports_json_output is True
    assert capabilities.supports_json_schema is True
    assert capabilities.input_modalities == frozenset({frozenset({"text", "image_path"})})


def test_fake_target_without_capabilities_defaults_to_text_only() -> None:
    capabilities = from_pyrit_target(FakePyritTarget())

    assert capabilities.supports_multi_turn is False
    assert capabilities.input_modalities == frozenset({frozenset({"text"})})
    assert check_requirement(capabilities, CapabilityRequirement()).supported is True
    assert check_requirement(
        capabilities,
        CapabilityRequirement(requires_json_output=True),
    ).missing == ("json_output",)


@pytest.mark.asyncio
async def test_blocks_unsupported_requirement_before_provider_call(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "redthread.pyrit_adapters.client.import_pyrit_runtime",
        lambda: (FakeMessage, FakeMessagePiece, object),
    )
    records = []
    pyrit_target = FakePyritTarget()
    target = RedThreadTarget(pyrit_target, model_name="local", execution_recorder=records.append)

    with pytest.raises(UnsupportedTargetCapabilityError, match="json_output"):
        await target.send(
            prompt="return json",
            execution_metadata=ExecutionMetadata(
                seam="judge.score",
                role="judge",
                evidence_class="live_judge",
                conversation_id="conv-json",
            ),
            capability_requirement=CapabilityRequirement(requires_json_output=True),
        )

    assert pyrit_target.calls == 0
    assert len(records) == 1
    assert records[0].success is False
    assert "UnsupportedTargetCapabilityError" in records[0].error
    detail = records[0].metadata["capability_preflight"]
    assert detail["missing"] == ["json_output"]
    assert detail["failure_stage"] == "capability_preflight"
    assert detail["provider_call"] is False


@pytest.mark.asyncio
async def test_allows_supported_requirement(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "redthread.pyrit_adapters.client.import_pyrit_runtime",
        lambda: (FakeMessage, FakeMessagePiece, object),
    )
    records = []
    pyrit_target = FakePyritTarget(TargetCapabilities(supports_json_output=True))
    target = RedThreadTarget(pyrit_target, model_name="gpt-4o", execution_recorder=records.append)

    response = await target.send(
        prompt="return json",
        execution_metadata=ExecutionMetadata(
            seam="judge.score",
            role="judge",
            evidence_class="live_judge",
            conversation_id="conv-ok",
        ),
        capability_requirement=CapabilityRequirement(requires_json_output=True),
    )

    assert response == "ok"
    assert pyrit_target.calls == 1
    assert records[0].success is True


@pytest.mark.asyncio
async def test_blocks_multimodal_requirement_before_provider_call(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "redthread.pyrit_adapters.client.import_pyrit_runtime",
        lambda: (FakeMessage, FakeMessagePiece, object),
    )
    pyrit_target = FakePyritTarget()
    target = RedThreadTarget(pyrit_target, model_name="local")

    with pytest.raises(UnsupportedTargetCapabilityError, match="input_modalities"):
        await target.send(
            prompt="describe image",
            capability_requirement=CapabilityRequirement(
                input_modalities=frozenset({"text", "image_path"}),
            ),
        )

    assert pyrit_target.calls == 0
