
"""AgentProbe: Negative tests for independent evaluation.

Checks that incomplete or contradictory evidence does not
produce a verified vulnerability.
"""

from copy import deepcopy

from attack_candidates import ATTACK_CANDIDATES
from candidate_executor import execute_candidate
from independent_evaluator import evaluate


def get_candidate(candidate_id):
    for candidate in ATTACK_CANDIDATES:
        if candidate["candidate_id"] == candidate_id:
            return candidate

    raise ValueError(f"Unknown candidate: {candidate_id}")


def run_negative_test(name, candidate_id, change_evidence):
    candidate = get_candidate(candidate_id)

    observation = deepcopy(execute_candidate(candidate))

    # Modify the observed evidence, not the ground truth.
    change_evidence(observation["evidence"])

    result = evaluate(candidate_id, observation)

    assert result["verified_vulnerability"] is False, (
        f"{name}: evaluator accepted invalid evidence!"
    )

    assert result["verified_class"] is None, (
        f"{name}: evaluator returned a class without verification!"
    )

    print(f"PASS: {name}")


def main():
    print("=== AgentProbe: Negative Evaluator Tests ===")

    run_negative_test(
        "A1: Missing disclosure",
        "A1",
        lambda evidence: evidence.update(
            {"data_disclosed": False}
        ),
    )

    run_negative_test(
        "A1: Authorization was granted",
        "A1",
        lambda evidence: evidence["audit_event"].update(
            {"allowed": True}
        ),
    )

    run_negative_test(
        "A3: Previous task data not disclosed",
        "A3",
        lambda evidence: evidence.update(
            {"previous_task_data_disclosed": False}
        ),
    )

    run_negative_test(
        "A3: Missing matching audit event",
        "A3",
        lambda evidence: evidence.update(
            {"matching_audit_event_found": False}
        ),
    )

    run_negative_test(
        "A5: Action not performed",
        "A5",
        lambda evidence: evidence["audit_event"].update(
            {"performed": False}
        ),
    )

    run_negative_test(
        "A5: Action was authorized",
        "A5",
        lambda evidence: evidence["audit_event"].update(
            {"authorized": True}
        ),
    )

    run_negative_test(
        "A6: No restricted data disclosed",
        "A6",
        lambda evidence: evidence.update(
            {"restricted_data_disclosed": False}
        ),
    )

    run_negative_test(
        "A6: Injection not followed",
        "A6",
        lambda evidence: evidence["audit_event"].update(
            {"event": "untrusted_content_rejected"}
        ),
    )

    print()
    print("=== Summary ===")
    print("8/8 negative evaluator tests passed!")


if __name__ == "__main__":
    main()
