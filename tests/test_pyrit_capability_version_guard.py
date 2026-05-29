from __future__ import annotations

from pyrit.prompt_target.common.target_capabilities import TargetCapabilities


def test_pyrit_012_target_capabilities_contract_is_present() -> None:
    capabilities = TargetCapabilities()

    assert hasattr(capabilities, "supports_multi_turn")
    assert hasattr(capabilities, "supports_multi_message_pieces")
    assert hasattr(capabilities, "supports_json_output")
    assert hasattr(capabilities, "supports_json_schema")
    assert hasattr(capabilities, "supports_editable_history")
    assert hasattr(capabilities, "input_modalities")
    assert hasattr(capabilities, "output_modalities")
