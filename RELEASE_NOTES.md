# AgentProbe v2.0.0

AgentProbe v2 adds a controlled tool-response prompt-injection study to the existing AgentProbe repository. The original v1.0.0 source, results, tag, and history are retained.

## Included

- Three attack cases with clean and injected conditions for prompt extraction, terminal-role redirection, and debate/task redirection.
- An HF-002 comparison between an unfiltered tool response and a field-allowlist defense.
- Clean, English, German, and Italian experiment conditions.
- A ten-output evaluator audit CSV.
- One shared terminal-behavior detector used by each scorer and both offline audit scripts.
- Regression tests for bare, quoted, double-quoted, backticked, fenced, and clean outputs.
- Windows Docker reproduction instructions use Ollama llama3.2:latest at temperature 0, with Inspect model identifier ollama/llama3.2 and host.docker.internal:11434/v1.
- Pinned direct Python dependencies.

## Evaluator audit result

The ten HF-002 outputs were manually reviewed: human_label is 0 for all five clean outputs and 1 for all five injected outputs. The original detector labeled all ten outputs 0, producing five false negatives. The corrected detector identified all five injected outputs. This is a small, post-hoc regression audit, not an independent or held-out validation dataset. The counts apply only to these ten samples and do not establish detector accuracy beyond them.

## Limitations

The experiments use a fictional assistant, synthetic records, and a narrow behavioral detector. They do not establish real-world attack rates or general security performance. Raw Inspect evaluation logs are not included; see FINDINGS.md for the evidence boundaries and reproduction notes.
