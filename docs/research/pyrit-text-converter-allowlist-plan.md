# PyRIT Text Converter Allowlist Plan

Status: post-gate planning only. Do not implement converters in the current capability-gate tranche.

## Decision

Do not add converter runtime behavior now. The best RedThread fit is to keep the Phase 1–5 capability gate as the implementation boundary, then revisit converters only if replay evidence shows operator value.

If converters are added later, they must be a small, hidden, deterministic text-in/text-out allowlist behind existing attack strategy internals. They must not become CLI modes, report claims, scorer inputs, or a second PyRIT orchestration layer.

## Why this is the best fit

RedThread already has attack strategy generation and replay proof. Broad converter support would add feature volume before proof. The only useful converter role is narrow: generate controlled prompt variants inside an existing strategy path, then let RedThread judge, replay, and promotion gates decide truth.

## Candidate allowlist shape

Start with deterministic text-only converters whose behavior is easy to test and explain:

| Converter family | Why it may help | Keep out if |
| --- | --- | --- |
| Encoding transforms such as Base64 / ROT13 / Atbash / Morse | Useful for controlled obfuscation probes. | They create unsafe prompt-body storage or unclear replay semantics. |
| Character-level transforms such as spacing / diacritics / zero-width | Useful for guardrail robustness probes. | They harm benign utility too much. |
| Simple suffix/template converters | Useful for strategy composition when RedThread owns the template. | They become user-facing modes or duplicate RedThread prompt profiles. |
| JSON string escaping | Useful only for transport/schema probes. | It is mistaken for JSON response-mode support. |

Reject for this stage:
- LLM-backed converters
- random/non-deterministic converters
- audio/image/video/PDF/Word converters
- human-in-the-loop converters
- converter chains exposed to users
- any converter that writes PyRIT memory as authoritative evidence

## Future implementation guardrails

A future converter slice should add a RedThread-owned adapter, not pass PyRIT converter classes around the codebase.

Suggested seam:

```python
@dataclass(frozen=True)
class TextConverterSpec:
    name: str
    input_type: str = "text"
    output_type: str = "text"

async def apply_text_converter(prompt: str, spec: TextConverterSpec) -> str:
    ...
```

Rules:
- allowlist by stable RedThread names, not arbitrary class import strings
- assert converter input/output are both `text`
- record converter name in attack metadata only
- never treat converter output as confirmed evidence
- replay must use the exact converted prompt that was sent
- no new CLI flags until replay evidence proves operator need

## Tests required before any converter implementation

- allowlisted deterministic converter transforms text and records metadata
- non-allowlisted converter is rejected
- non-text converter is rejected
- LLM-backed converter is rejected
- random converter is rejected or forced deterministic
- replay uses exact converted text
- JudgeAgent and promotion semantics are unchanged

## Stop condition

Do not implement converters until there is a specific attack strategy or replay gap that capability gates do not solve. If the only reason is "PyRIT has many converters," reject the work.
