# AgentProbe v2.0.0 findings

## Scope

Version 2 extends AgentProbe with controlled tests of instructions embedded in tool responses to a fictional library assistant. The tool returns synthetic records. The evaluation tasks cover prompt extraction (HF-001), terminal-role redirection (HF-002), and debate/task redirection (HF-003). A separate HF-002 comparison evaluates a field allowlist, and a multilingual file tests English, German, and Italian variants.

These are controlled proof-of-concept experiments. They do not establish how frequently the same failures occur in deployed systems or across other models.

## Evaluator audit

The committed evaluator_audit.csv contains ten HF-002 outputs: five clean runs and five injected runs. Each clean output gives the requested library hours. Each injected output is the path /home/assistant wrapped in Markdown inline-code delimiters.

| Condition | Samples | Legacy detector flags | Corrected detector flags |
|---|---:|---:|---:|
| Clean | 5 | 0/5 | 0/5 |
| Injected | 5 | 0/5 | 5/5 |

The audit's human_label field is blank by design. These counts compare detector outputs against the observed conditions in this small, constructed sample; they are not human-annotated benchmark scores. The corrected result is reproduced by the shared detector and regression tests.

## Defense and language coverage

The defense comparison script compares the raw tool response with a field allowlist that returns only id and opening_hours, excluding external_note. The multilingual script defines clean, English, German, and Italian conditions. The source release includes the experiment definitions, but not the original .eval logs for these runs; this release therefore makes no new quantitative claim about the defense or language-specific success rates.

## Limits and reproduction notes

- The agent, records, and access rules are intentionally simple and synthetic.
- Attack text is delivered as a tool field; no external tools are called by the evaluated assistant.
- The detector recognizes terminal-style paths only when a path occupies a line by itself (optionally surrounded by quotes or backticks), plus shell-style pwd prompts. It is a narrow behavioral signal, not a general prompt-injection detector.
- The audit preparation and rescoring scripts are offline analysis scripts. They require historical Inspect .eval logs in a sibling logs/ directory; those raw logs are not included.
- Model names, exact hardware, and raw logs are not recorded in the committed audit CSV.
