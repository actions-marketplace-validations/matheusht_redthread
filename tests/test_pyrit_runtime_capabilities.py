from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from redthread.config.settings import TargetBackend
from redthread.pyrit_adapters.runtime import _build_pyrit_target


@dataclass(frozen=True)
class FakeCapabilities:
    supports_multi_turn: bool = False
    supports_multi_message_pieces: bool = False
    supports_json_output: bool = False
    supports_json_schema: bool = False
    supports_editable_history: bool = False
    input_modalities: frozenset[frozenset[str]] = frozenset({frozenset({"text"})})
    output_modalities: frozenset[frozenset[str]] = frozenset({frozenset({"text"})})


class FakeOpenAIChatTarget:
    def __init__(self, **kwargs: Any) -> None:
        self.kwargs = kwargs
        self.capabilities = kwargs.get("custom_capabilities") or FakeCapabilities(
            supports_multi_turn=True,
            supports_multi_message_pieces=True,
            supports_json_output=True,
        )


def _patch_runtime(monkeypatch) -> None:
    monkeypatch.setattr("redthread.pyrit_adapters.runtime.ensure_pyrit_memory_initialized", lambda: None)
    monkeypatch.setattr(
        "redthread.pyrit_adapters.runtime.import_pyrit_runtime",
        lambda: (object, object, FakeOpenAIChatTarget),
    )
    monkeypatch.setattr(
        "redthread.pyrit_adapters.runtime.import_pyrit_target_capabilities",
        lambda: FakeCapabilities,
    )


def test_openai_target_passes_underlying_model_for_known_capability_lookup(monkeypatch) -> None:
    _patch_runtime(monkeypatch)

    target = _build_pyrit_target(
        backend=TargetBackend.OPENAI,
        model="gpt-4o",
        base_url="",
        api_key="test-key",
    )

    assert target.kwargs["underlying_model"] == "gpt-4o"
    assert "custom_capabilities" not in target.kwargs


def test_ollama_target_uses_text_chat_capabilities_without_json_claim(monkeypatch) -> None:
    _patch_runtime(monkeypatch)

    target = _build_pyrit_target(
        backend=TargetBackend.OLLAMA,
        model="llama3",
        base_url="http://localhost:11434",
    )

    assert target.kwargs["custom_capabilities"].supports_multi_turn is True
    assert target.kwargs["custom_capabilities"].supports_multi_message_pieces is True
    assert target.kwargs["custom_capabilities"].supports_json_output is False


def test_llama_cpp_target_uses_text_chat_capabilities_without_json_claim(monkeypatch) -> None:
    _patch_runtime(monkeypatch)

    target = _build_pyrit_target(
        backend=TargetBackend.LLAMA_CPP,
        model="local.gguf",
        base_url="http://localhost:8080",
    )

    assert target.kwargs["custom_capabilities"].supports_multi_turn is True
    assert target.kwargs["custom_capabilities"].supports_multi_message_pieces is True
    assert target.kwargs["custom_capabilities"].supports_json_output is False
