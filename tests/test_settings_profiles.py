"""Tests for flat env-compatible settings profiles."""

from __future__ import annotations

from pytest import MonkeyPatch

from redthread.config.settings import AlgorithmType, RedThreadSettings, SettingsProfile


def test_ci_profile_applies_minimal_low_cost_defaults_without_env_file() -> None:
    settings = RedThreadSettings(_env_file=None, profile=SettingsProfile.CI)

    assert settings.dry_run is True
    assert settings.telemetry_enabled is False
    assert settings.tree_depth == 2
    assert settings.branching_factor == 2
    assert settings.mcts_simulations == 5


def test_profile_does_not_override_explicit_constructor_values() -> None:
    settings = RedThreadSettings(_env_file=None, profile=SettingsProfile.CI, dry_run=False)

    assert settings.dry_run is False
    assert settings.tree_depth == 2


def test_flat_redthread_environment_names_still_work(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv("REDTHREAD_DRY_RUN", "true")
    monkeypatch.setenv("REDTHREAD_ALGORITHM", "tap")
    monkeypatch.setenv("REDTHREAD_OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("REDTHREAD_LOG_DIR", "custom-logs")
    monkeypatch.setenv("REDTHREAD_MEMORY_DIR", "custom-memory")

    settings = RedThreadSettings(_env_file=None)

    assert settings.dry_run is True
    assert settings.algorithm == AlgorithmType.TAP
    assert settings.openai_api_key == "test-key"
    assert str(settings.log_dir) == "custom-logs"
    assert str(settings.memory_dir) == "custom-memory"


def test_with_profile_returns_profile_overlay_copy() -> None:
    settings = RedThreadSettings(_env_file=None, dry_run=False).with_profile("ci")

    assert settings.profile == SettingsProfile.CI
    assert settings.dry_run is True
    assert settings.tree_width == 3
