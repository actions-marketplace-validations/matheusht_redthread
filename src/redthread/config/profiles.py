"""Minimal settings profiles for operator surfaces."""

from __future__ import annotations

from typing import Any

from redthread.config.types import SettingsProfile

PROFILE_OVERRIDES: dict[SettingsProfile, dict[str, Any]] = {
    SettingsProfile.DEFAULT: {},
    SettingsProfile.RESEARCH: {
        "dry_run": False,
        "telemetry_enabled": True,
        "mcts_simulations": 100,
        "mcts_max_budget_tokens": 1_000_000,
    },
    SettingsProfile.CI: {
        "dry_run": True,
        "telemetry_enabled": False,
        "max_iterations": 3,
        "tree_depth": 2,
        "tree_width": 3,
        "branching_factor": 2,
        "crescendo_max_turns": 3,
        "mcts_simulations": 5,
        "mcts_max_budget_tokens": 50_000,
    },
}


def profile_overrides(profile: SettingsProfile | str) -> dict[str, Any]:
    """Return a copy of overrides for one profile."""
    return dict(PROFILE_OVERRIDES[SettingsProfile(profile)])


__all__ = ["PROFILE_OVERRIDES", "SettingsProfile", "profile_overrides"]
