# AgentProbe

AgentProbe is a research prototype for controlled red-team experiments against tool-using assistants. The repository preserves the original v1.0.0 experiment and history, and adds the v2.0.0 tool-response injection study.

## Version 1.0.0

The original release compares fixed, adaptive, and random test selection across six candidates, including four planted vulnerability scenarios and two safe controls. Each strategy receives two candidate executions per run across twelve candidate orderings.

| Metric | Fixed | Adaptive | Random |
|---|---:|---:|---:|
| Mean distinct verified classes | 0.667 | 1.417 | 1.250 |
| Mean internal tool calls | 2.333 | 2.833 | 2.250 |
| Safe controls passed/tested | 16/16 | 7/7 | 9/9 |

In those controlled runs, the adaptive strategy found the most distinct vulnerability classes on average, while making more internal tool calls than the random strategy. The results do not establish lower cost across all measures or performance against real-world agents.

## Version 2.0.0

The v2 experiments use a fictional library assistant whose lookup tool can return a synthetic attacker-controlled note. The package includes three attack cases with clean and injected conditions, an HF-002 defense comparison, English/German/Italian variants, an evaluator audit CSV, and scripts for examining historical Inspect logs.

See FINDINGS.md for the reported audit counts and limitations. The findings are deliberately narrow: the experiments do not estimate real-world attack rates or establish general model security.

## Files

| File | Purpose |
|---|---|
| inspect_attack_batch_v2.py | Clean and injected conditions for HF-001, HF-002, and HF-003 |
| inspect_defense_comparison.py | HF-002 baseline versus field-allowlist comparison |
| inspect_multilingual_attacks.py | Clean, English, German, and Italian conditions |
| terminal_redirection.py | Shared terminal-behavior detector for scorers and offline audit scripts |
| tests/test_terminal_redirection.py | Regression tests for bare, quoted, backticked, and fenced paths |
| attack_batch.json | Attack text, source rows, and task metadata |
| evaluator_audit.csv | Ten recorded HF-002 outputs and old/corrected detector outputs |
| prepare_evaluator_audit.py, rescore_hf002.py | Offline analysis of historical Inspect logs |
| Dockerfile, requirements.txt | Pinned direct Python dependencies and container setup |

The earlier v1.0.0 source and result files remain in the repository. No v1 files need to be replaced to run v2.

## Requirements

- Docker Desktop on Windows, with its Linux container engine running
- Ollama running on the Windows host and a model already downloaded
- The pinned Python packages in requirements.txt (the Docker image installs them)

The source pins inspect-ai==0.3.287 and openai==3.42.1, matching the available AgentProbe environment. The Docker image uses Python 3.12.

## Build and run on Windows

From PowerShell, change into the repository folder and build the image:

```powershell
docker build -t agentprobe:v2.0.0 .
```

Check the exact model name with ollama list. This Windows setup has qwen2:7b installed; change the model argument if needed:

```powershell
docker run --rm `
  -e OLLAMA_BASE_URL=http://host.docker.internal:11434/v1 `
  -v "${PWD}:/app" `
  agentprobe:v2.0.0 `
  inspect eval inspect_attack_batch_v2.py@hf002_injected --model ollama/qwen2:7b
```

The bind mount keeps new Inspect logs in the repository's local logs/ directory. host.docker.internal lets the container reach Ollama on Windows. To run a different task, replace hf002_injected with a task name from the corresponding script. To run every task in a script, omit the @task_name suffix.

## Regression tests

The detector regression tests use only the Python standard library:

```powershell
python -m unittest discover -s tests -v
```

## Historical audit scripts

The audit preparation and rescoring scripts read original HF-002 Inspect logs from logs/. The source release does not bundle those logs; place the matching historical files there before running either script. The committed evaluator_audit.csv remains available for review without them.
