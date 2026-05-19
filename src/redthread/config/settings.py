"""Global RedThread configuration loaded from TOML/.env and environment variables."""

from __future__ import annotations

from typing import Any

from pydantic_settings import BaseSettings, SettingsConfigDict

from redthread.config.profiles import profile_overrides
from redthread.config.settings_groups import (
    AlgorithmBudgetSettings,
    ModelEndpointSettings,
    RuntimeStorageSettings,
    TelemetrySettings,
)
from redthread.config.types import (
    AlgorithmType,
    CanaryPolicyPreset,
    ModelRole,
    SettingsProfile,
    TargetBackend,
)


class RedThreadSettings(
    ModelEndpointSettings,
    AlgorithmBudgetSettings,
    RuntimeStorageSettings,
    TelemetrySettings,
    BaseSettings,
):
    """Flat env-compatible RedThread settings facade.

    The field groups keep concern boundaries readable, but this class remains the
    only public BaseSettings surface so existing `REDTHREAD_*` env vars continue
    to work. Profiles are simple overlays, not nested schemas.
    """

    model_config = SettingsConfigDict(
        env_prefix="REDTHREAD_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    profile: SettingsProfile = SettingsProfile.DEFAULT

    def model_post_init(self, __context: Any) -> None:
        """Apply minimal profile defaults without overriding explicit values."""
        fields_set = self.model_fields_set
        for field_name, value in profile_overrides(self.profile).items():
            if field_name not in fields_set:
                object.__setattr__(self, field_name, value)

    def with_profile(self, profile: SettingsProfile | str) -> RedThreadSettings:
        """Return a copied settings object with one profile overlay applied."""
        updates = {"profile": SettingsProfile(profile), **profile_overrides(profile)}
        return self.model_copy(update=updates)


__all__ = [
    "AlgorithmType",
    "CanaryPolicyPreset",
    "ModelRole",
    "RedThreadSettings",
    "SettingsProfile",
    "TargetBackend",
]
