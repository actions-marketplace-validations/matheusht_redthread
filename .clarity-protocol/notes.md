# Notes

RedThread should use PyRIT as bounded infrastructure plumbing only. The current PyRIT work is approved for capability-gate implementation as the first slice. Converter work stays out of the first slice and can be planned later as a small text-only allowlist after capability gates land. Unsupported capability failures should be recorded in logs/execution records only, not promoted into the operator report summary.

Implementation note: PyRIT adapter Phases 1–6 are complete for this tranche. OpenAI targets pass `underlying_model=model` for known PyRIT capability lookup. Ollama and llama.cpp targets use conservative text-chat custom capabilities and do not claim JSON output by default. Phase 6 is planning only: converter runtime behavior remains deferred behind `docs/research/pyrit-text-converter-allowlist-plan.md`.
