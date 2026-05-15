from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest

from redthread.research.source_mutation_artifacts import (
    apply_patch_payload,
    matches_payload,
    sha256,
)
from redthread.research.source_mutation_models import PatchFileArtifact
from redthread.research.source_mutation_revert import matches_fingerprints


def test_apply_patch_payload_rejects_parent_escape(tmp_path: Path) -> None:
    rel_path, outside = _outside_ref(tmp_path)
    payload = [PatchFileArtifact(path=rel_path, content="owned", sha256=sha256("owned"))]

    with pytest.raises(ValueError, match="escapes workspace"):
        apply_patch_payload(tmp_path, payload)

    assert not outside.exists()


def test_apply_patch_payload_rejects_absolute_path(tmp_path: Path) -> None:
    absolute = tmp_path / "absolute.txt"
    payload = [PatchFileArtifact(path=str(absolute), content="owned", sha256=sha256("owned"))]

    with pytest.raises(ValueError, match="workspace-relative"):
        apply_patch_payload(tmp_path, payload)

    assert not absolute.exists()


def test_matches_payload_rejects_parent_escape(tmp_path: Path) -> None:
    rel_path, outside = _outside_ref(tmp_path)
    outside.write_text("secret", encoding="utf-8")
    payload = [PatchFileArtifact(path=rel_path, content="secret", sha256=sha256("secret"))]

    with pytest.raises(ValueError, match="escapes workspace"):
        matches_payload(tmp_path, payload)


def test_matches_fingerprints_rejects_parent_escape(tmp_path: Path) -> None:
    rel_path, outside = _outside_ref(tmp_path)
    outside.write_text("secret", encoding="utf-8")

    with pytest.raises(ValueError, match="escapes workspace"):
        matches_fingerprints(tmp_path, {rel_path: sha256("secret")}, sha256)


def _outside_ref(root: Path) -> tuple[str, Path]:
    outside = root.parent / f"{root.name}-escape-{uuid4().hex}.txt"
    return f"../{outside.name}", outside
