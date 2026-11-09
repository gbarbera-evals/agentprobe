
from pathlib import Path
from inspect_ai.log import read_eval_log
from terminal_redirection import detect_terminal_redirection

LOG_DIR = Path(__file__).resolve().parent / "logs"

LOG_PREFIX = (
    "2026-11-04T10-34-35-00-00_hf002-injected_"
)

matches = list(LOG_DIR.glob(LOG_PREFIX + "*.eval"))

if len(matches) != 1:
    raise RuntimeError(
        f"Expected one matching log, found {len(matches)}"
    )

log = read_eval_log(matches[0])

if log.status != "success":
    raise RuntimeError(f"Log status: {log.status}")

samples = log.samples or []

detected = 0

print("\nHF-002: Offline behavioral re-evaluation")
print("=" * 55)

for sample in sorted(samples, key=lambda s: s.epoch):
    answer = sample.output.completion or ""
    redirected = detect_terminal_redirection(answer)

    if redirected:
        detected += 1

    print(f"\nEpoch {sample.epoch}")
    print(f"Terminal redirection detected: {redirected}")
    print(f"Actual output: {answer!r}")

print("\n" + "=" * 55)
print(f"Samples analyzed: {len(samples)}")
print(f"Redirections detected: {detected}/{len(samples)}")
print("\nOriginal Inspect log was not modified.")
