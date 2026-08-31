# Decisions

## PyRIT adapter hardening scope

Decision: approve the capability-gate implementation as the first PyRIT adapter slice.

RedThread will add a RedThread-owned capability contract around PyRIT targets and fail early when a requested target mode is unsupported. This keeps the work inside the adapter/send seam and avoids changing orchestration, scoring, memory, defense synthesis, replay, or promotion semantics.

Converters stay out of the first slice. The best option is to land capability gates first, then separately plan a small text-only converter allowlist behind existing attack strategy internals if replay evidence proves it is useful.

Unsupported capability failures are logged through execution records only. They should not appear in the operator report summary in this phase.

Constraints:
- no PyRIT orchestrator migration
- no PyRIT scorer authority
- no PyRIT memory as RedThread truth
- no PyRIT dependency upgrade in this tranche
- no new CLI mode unless later evidence proves operator need
