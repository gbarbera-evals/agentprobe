# AgentProbe v2.0.0

AgentProbe v2 adds a controlled tool-response prompt-injection study to the existing AgentProbe repository. The original v1.0.0 source, results, tag, and history are retained.

## Included

- Three attack cases with clean and injected conditions for prompt extraction, terminal-role redirection, and debate/task redirection.
- An HF-002 comparison between an unfiltered tool response and a field-allowlist defense.
- Clean, English, German, and Italian experiment conditions.
- A ten-output evaluator audit CSV.
- One shared terminal-behavior detector used by each scorer and both offline audit scripts.
- Regression tests for bare, quoted, double-quoted, backticked, fenced, and clean outputs.
- Windows Docker instructions for running Inspect AI with Ollama through host.docker.internal.
- Pinned direct Python dependencies.

## Evaluator audit result

In the included ten-output HF-002 audit, the legacy detector flags none of the five injected backticked paths, while the corrected detector flags all five. Neither detector flags the five clean answers. The audit's human labels are intentionally blank; the counts are detector results on this small constructed sample, not human-annotated benchmark scores.

## Limitations

The experiments use a fictional assistant, synthetic records, and a narrow behavioral detector. They do not establish real-world attack rates or general security performance. Raw Inspect evaluation logs are not included; see FINDINGS.md for the evidence boundaries and reproduction notes.
