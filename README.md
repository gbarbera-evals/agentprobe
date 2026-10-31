# AgentProbe

**A reproducible proof-of-concept benchmark for outcome-guided red teaming of tool-using AI agents.**

AgentProbe investigates whether an adaptive test-selection strategy can identify distinct security failure classes more effectively than fixed and random strategies under a limited testing budget.

The project uses deterministic mock tools, synthetic data, deliberately planted vulnerabilities, and an independent evidence-based evaluator.

## Research Question

Can an adaptive red-teaming strategy discover distinct security failures in a tool-using AI agent more efficiently than a fixed attack suite under the same testing budget?

## Experimental Design

AgentProbe compares three strategies:

- **Fixed:** Executes candidates in a predetermined order.
- **Adaptive:** Selects subsequent tests based on observed outcomes and predefined test-category preferences.
- **Random:** Selects candidates randomly using reproducible seeds.

The benchmark contains six candidates, including four planted vulnerability scenarios and two safe controls.

Each strategy receives a budget of two candidate executions per run. The experiment uses 12 unique candidate orderings.

## Results

| Metric | Fixed | Adaptive | Random |
|---|---:|---:|---:|
| Mean distinct verified classes | 0.667 | 1.417 | 1.250 |
| Mean internal tool calls | 2.333 | 2.833 | 2.250 |
| Safe controls passed/tested | 16/16 | 7/7 | 9/9 |

The adaptive strategy achieved the highest mean vulnerability-class discovery under the candidate-execution budget.

However, it also required more internal tool calls than the random baseline. The results therefore do not establish superior efficiency under every cost measure.

## Evaluation

An independent evaluator checks execution evidence against predefined verification rules.

The current test suite includes six positive fixture checks and eight negative evidence checks, all passing in the final local runs.

## Limitations

AgentProbe is a controlled research prototype, not a production red-teaming platform.

- Vulnerabilities are deliberately planted in deterministic mock implementations.
- The adaptive strategy is a hand-designed heuristic, not a learned or autonomous attack policy.
- The experiment uses 12 orderings of the same six candidates, not independent vulnerability environments.
- Equal candidate-execution budgets do not imply equal internal tool-call costs.
- Results do not establish performance against real-world LLM agents.
- PyRIT is not integrated into the final benchmark.

## Reproducibility

The experiment uses fixed random seeds and writes structured JSON results. Two consecutive local executions produced matching candidate selections and aggregate statistics.