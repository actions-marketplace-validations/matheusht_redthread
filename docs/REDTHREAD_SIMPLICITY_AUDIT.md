# RedThread Simplicity Audit

Date: 2026-05-18  
Scope: Phase 0 through Phase 13 simplicity work  
Status: implementation freeze recommended; no Phase 14 included

## Executive finding

RedThread is now simpler on the operator path without weakening evidence honesty.

The product spine is clear:

`attack → judge → defend → replay → promotion evidence`

The main outcome is not fewer capabilities. The outcome is fewer default choices, clearer proof language, and stronger boundaries between candidate defenses, validated candidates, promotable defenses, and active guardrails.

## What changed

### Phase 0 — Baseline proof and cut list

Established the simplicity target: keep the core attack/judge/defend/replay/promotion loop and avoid exposing research complexity by default.

### Phase 1 — Golden operator path

`redthread run` now has a clearer default report path:

- live/default: `reports/<campaign_id>/`
- dry-run: `reports/<campaign_id>/dry-run/`
- explicit override: `--report-dir <path>`

CLI help now separates normal, advanced, and research-oriented flags.

### Phase 2 — Evidence vocabulary

Evidence labels now distinguish live proof, sealed dry-run proof, weak hints, validated candidates, promotable defenses, and active guardrails.

Operator reports include evidence counts and uncertainty notes.

### Phase 3 — Supervisor spine

The supervisor was split into smaller modules while keeping `redthread.orchestration.supervisor` as the compatibility facade.

This reduced the core orchestration surface without removing behavior.

### Phase 4 — Attack runner registry

Attack execution now routes through a small runner registry.

TAP has smoke/safety coverage instead of a weak empty test.

### Phase 5 — Defense boundary

Defense synthesis writes `validated_candidate` records.

Runtime injection only reads `active_guardrail` records.

This prevents replay-passed candidates from being described as deployed controls.

### Phase 6 — Settings/profile simplification

Settings were split into smaller files while keeping a flat env-compatible facade.

Profiles are minimal:

- `default`
- `research`
- `ci`

Explicit constructor/env/`.env` values still win over profile overlays.

### Phase 7 — Product docs and wiki cleanup

README, product docs, and wiki pages now describe RedThread as an evidence workflow, not a research-lab maze.

### Phase 8 — Deletion/deprecation pass

Compatibility surfaces were kept where removal would be premature.

No API-breaking cleanup was hidden inside the simplicity work.

### Phase 9 — Alias centralization

Defense state aliases are centralized in `src/redthread/core/defense_status.py`.

Canonical terms:

- `validated_candidate`
- `defense_validated_candidates`

Deprecated compatibility aliases retained:

- `defense_deployed`
- `defense_deployments`

### Phase 10 — Operator proof UX

Markdown reports now start with:

- `## Executive Summary`
- `## Why Trust This Report`
- `## What To Do Next`

The report leads with confirmed findings, run count, attack success rate, JudgeAgent average score, evidence mode, promotion state, and proof path.

### Phase 11 — Promotion workflow hardening

Promotion now uses the explicit ladder:

`candidate_defense → validated_candidate → promotable_defense → active_guardrail`

Promotion validation writes:

- `promotion_state_by_trace`
- `promotion_evidence_mode_by_trace`

Sealed dry-run evidence and live validation errors fail closed.

### Phase 12 — Promotion proof readout

`redthread research promote` and `redthread research promote-inspect` now show:

- outcome
- ladder
- state counts
- trace state
- evidence mode
- failure buckets

Successful promotion says `active_guardrail written: N`.

Dry-run clearly says no production memory write occurred.

### Phase 13 — Runtime active-guardrail audit proof

Runtime injection now writes non-secret audit events to `logs/guardrail_audit.jsonl`.

Audit events include:

- action
- active guardrail count
- active trace IDs
- clause hashes
- target model
- prompt hash
- source

Raw guardrail clause text is not needed in the audit event.

## Evidence honesty check

No evidence overclaim was found in the Phase 0–13 design.

Important boundaries are preserved:

- JudgeAgent owns confirmed jailbreak findings.
- Detector hints remain weak signals, not verdicts.
- Sealed dry-run replay is useful evidence, not live production proof.
- `validated_candidate` is not an active guardrail.
- `promotable_defense` is not an active guardrail.
- `active_guardrail` appears only after explicit promotion.
- Runtime injection loads only active guardrails.
- Audit proof uses hashes and trace IDs, not raw clause text.

Remaining compatibility debt is named, not hidden:

- `DeploymentRecord` is still the compatibility type name.
- `defense_deployed` remains a deprecated alias.
- `defense_deployments` remains a deprecated alias.

## Operator path check

The default path is still simple:

1. run campaign
2. open report
3. read executive summary
4. inspect why to trust it
5. decide next action
6. promote only with explicit evidence

Research and advanced controls still exist, but they are not the default operator experience.

## Validation performed

Post-Phase 13 validation passed:

- `.venv/bin/python -m pytest -q` → `636 passed, 1 skipped`
- `.venv/bin/ruff check src tests` → passed
- `python3 scripts/wiki_lint.py` → passed
- `implementation-notes.html` parse → passed
- manual dry-run report smoke → passed at `/tmp/redthread-audit-report/campaign-7f04a9d9/dry-run/operator-report.md`

Manual report inspection confirmed the top sections are present:

- `## Executive Summary`
- `## Why Trust This Report`
- `## What To Do Next`
- `## Evidence & Uncertainty`

## Repo-state note

Unrelated local files were not deleted.

Known unrelated/unreviewed files include examples such as `false`, outreach docs, and unrelated research drafts. They should stay out of the simplicity PR unless separately reviewed.

## Recommendation

Freeze implementation here.

Next work should be PR review, manual report inspection, and cleanup decisions.

Do not start Phase 14 until a specific release goal is approved.

Possible later Phase 14 options:

- API-breaking cleanup for `DeploymentRecord`, `defense_deployed`, and `defense_deployments`
- report JSON v2 with promotion proof fields
- end-to-end operator demo fixture
- packaging and release-readiness pass
