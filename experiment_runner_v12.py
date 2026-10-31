
"""AgentProbe v12: Reproducible strategy comparison.

Synthetic proof-of-concept benchmark comparing fixed,
adaptive, and random red-teaming test selection.
"""

import json
import random
import statistics
from pathlib import Path

from attack_candidates import ATTACK_CANDIDATES, DEFAULT_BUDGET
from candidate_executor import execute_candidate
from independent_evaluator import evaluate
from ground_truth import GROUND_TRUTH


ORDERING_COUNT = 12
ORDERING_SEED = 42
RANDOM_SEED_BASE = 10000
STRATEGIES = ("fixed", "adaptive", "random")


def public_candidate(candidate):
    """Remove ground-truth class labels from selector input."""
    return {
        key: value
        for key, value in candidate.items()
        if key != "vulnerability_class"
    }


def generate_orderings(candidates):
    """Generate unique, reproducible candidate orderings."""
    rng = random.Random(ORDERING_SEED)

    orderings = [list(candidates)]
    seen = {
        tuple(c["candidate_id"] for c in candidates)
    }

    while len(orderings) < ORDERING_COUNT:
        ordering = list(candidates)
        rng.shuffle(ordering)

        key = tuple(c["candidate_id"] for c in ordering)

        if key not in seen:
            seen.add(key)
            orderings.append(ordering)

    return orderings


def choose_candidate(strategy, affordable, history, rng):
    """Choose the next candidate without evaluator ground truth."""

    if strategy == "fixed":
        return affordable[0]

    if strategy == "random":
        return rng.choice(affordable)

    if strategy == "adaptive":
        disclosure_seen = any(
            entry["evidence"].get("data_disclosed") is True
            or entry["evidence"].get(
                "previous_task_data_disclosed"
            ) is True
            or entry["evidence"].get(
                "restricted_data_disclosed"
            ) is True
            for entry in history
        )

        if disclosure_seen:
            for preferred_type in (
                "cross_task_leakage",
                "indirect_prompt_injection",
            ):
                for candidate in affordable:
                    if candidate["test_type"] == preferred_type:
                        return candidate

        tested_types = {
            entry["test_type"] for entry in history
        }

        for candidate in affordable:
            if candidate["test_type"] not in tested_types:
                return candidate

        return affordable[0]

    raise ValueError(f"Unknown strategy: {strategy}")


def run_strategy(strategy, ordering, budget, seed):
    """Run one strategy and record its results."""

    rng = random.Random(seed)

    remaining = [
        public_candidate(candidate)
        for candidate in ordering
    ]

    history = []
    budget_used = 0

    while remaining:
        affordable = [
            candidate for candidate in remaining
            if budget_used + candidate["budget_cost"] <= budget
        ]

        if not affordable:
            break

        candidate = choose_candidate(
            strategy, affordable, history, rng
        )

        observation = execute_candidate(candidate)
        score = evaluate(
            candidate["candidate_id"], observation
        )

        entry = {
            "candidate_id": candidate["candidate_id"],
            "test_type": candidate["test_type"],
            "budget_cost": candidate["budget_cost"],
            "internal_tool_calls": observation["internal_tool_calls"],
            "evidence": observation["evidence"],
            "verified_vulnerability": score["verified_vulnerability"],
            "verified_class": score["verified_class"],
            "is_safe_control": score["is_safe_control"],
            "safe_control_passed": score["safe_control_passed"],
        }

        history.append(entry)
        budget_used += candidate["budget_cost"]

        remaining = [
            item for item in remaining
            if item["candidate_id"] != candidate["candidate_id"]
        ]

    verified_classes = sorted({
        entry["verified_class"]
        for entry in history
        if entry["verified_vulnerability"]
        and entry["verified_class"] is not None
    })

    controls = [
        entry for entry in history
        if entry["is_safe_control"]
    ]

    controls_passed = sum(
        entry["safe_control_passed"]
        for entry in controls
    )

    return {
        "strategy": strategy,
        "random_seed": seed if strategy == "random" else None,
        "budget_limit": budget,
        "budget_used": budget_used,
        "tests_executed": len(history),
        "internal_tool_calls": sum(
            entry["internal_tool_calls"]
            for entry in history
        ),
        "distinct_verified_classes": len(verified_classes),
        "verified_classes": verified_classes,
        "safe_controls_tested": len(controls),
        "safe_controls_passed": controls_passed,
        "safe_controls_failed": len(controls) - controls_passed,
        "selected_candidates": [
            entry["candidate_id"]
            for entry in history
        ],
        "unselected_candidates": [
            candidate["candidate_id"]
            for candidate in remaining
        ],
        "results": history,
    }


def validate_registry():
    """Validate candidate IDs and ground truth."""

    ids = [
        candidate["candidate_id"]
        for candidate in ATTACK_CANDIDATES
    ]

    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate candidate IDs.")

    if set(ids) != set(GROUND_TRUTH):
        raise ValueError(
            "Candidate registry and ground truth do not match."
        )

    if DEFAULT_BUDGET <= 0:
        raise ValueError("Budget must be positive.")

    if ORDERING_COUNT > 720:
        raise ValueError(
            "Too many orderings for this six-candidate benchmark."
        )


def aggregate_results(all_runs):
    """Calculate strategy-level statistics."""

    summary = []

    for strategy in STRATEGIES:
        runs = [
            run for run in all_runs
            if run["strategy"] == strategy
        ]

        discoveries = [
            run["distinct_verified_classes"]
            for run in runs
        ]

        calls = [
            run["internal_tool_calls"]
            for run in runs
        ]

        summary.append({
            "strategy": strategy,
            "runs": len(runs),
            "mean_distinct_verified_classes": round(
                statistics.mean(discoveries), 3
            ),
            "standard_deviation": round(
                statistics.stdev(discoveries), 3
            ),
            "mean_internal_tool_calls": round(
                statistics.mean(calls), 3
            ),
            "total_safe_controls_tested": sum(
                run["safe_controls_tested"]
                for run in runs
            ),
            "total_safe_controls_passed": sum(
                run["safe_controls_passed"]
                for run in runs
            ),
            "total_safe_controls_failed": sum(
                run["safe_controls_failed"]
                for run in runs
            ),
        })

    return summary


def main():
    validate_registry()

    # FIXED: Pass the candidate list to the function.
    orderings = generate_orderings(ATTACK_CANDIDATES)

    all_runs = []

    print("=== AgentProbe v12: Final Experiment ===")
    print(f"Candidates: {len(ATTACK_CANDIDATES)}")
    print(f"Budget per strategy: {DEFAULT_BUDGET}")
    print(f"Orderings: {len(orderings)}")
    print()

    for index, ordering in enumerate(orderings, start=1):
        ordering_ids = [
            candidate["candidate_id"]
            for candidate in ordering
        ]

        print(f"Ordering {index:02d}: {ordering_ids}")

        for strategy in STRATEGIES:
            seed = RANDOM_SEED_BASE + index

            result = run_strategy(
                strategy,
                ordering,
                DEFAULT_BUDGET,
                seed
            )

            result["ordering_number"] = index
            result["candidate_order"] = ordering_ids

            all_runs.append(result)

            print(
                f"  {strategy.upper():8} "
                f"classes={result['distinct_verified_classes']} "
                f"controls={result['safe_controls_passed']}/"
                f"{result['safe_controls_tested']} "
                f"budget={result['budget_used']} "
                f"calls={result['internal_tool_calls']} "
                f"selected={result['selected_candidates']}"
            )

        print()

    aggregate = aggregate_results(all_runs)

    print("=== Aggregate Results ===")

    for item in aggregate:
        print(
            f"{item['strategy'].upper():8} "
            f"mean_classes="
            f"{item['mean_distinct_verified_classes']:.3f} "
            f"std={item['standard_deviation']:.3f} "
            f"mean_calls="
            f"{item['mean_internal_tool_calls']:.3f} "
            f"controls="
            f"{item['total_safe_controls_passed']}/"
            f"{item['total_safe_controls_tested']}"
        )

    output = {
        "experiment": "AgentProbe v12",
        "configuration": {
            "candidate_count": len(ATTACK_CANDIDATES),
            "budget_per_strategy": DEFAULT_BUDGET,
            "ordering_count": ORDERING_COUNT,
            "ordering_seed": ORDERING_SEED,
            "random_seed_base": RANDOM_SEED_BASE,
            "strategies": list(STRATEGIES),
        },
        "limitations": [
            "Synthetic deterministic mock environment.",
            "Four deliberately planted vulnerability classes.",
            "Twelve orderings of the same six candidates.",
            "Equal candidate budgets, not equal internal tool calls.",
            "No generalization to real-world agents established.",
        ],
        "aggregate": aggregate,
        "runs": all_runs,
    }

    output_path = Path(__file__).with_name(
        "strategy_comparison_v12.json"
    )

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(output, file, indent=4)

    print()
    print(f"Results saved: {output_path}")


if __name__ == "__main__":
    main()
