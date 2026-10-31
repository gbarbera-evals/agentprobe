
"""AgentProbe: Tests for the independent evaluator."""

from attack_candidates import ATTACK_CANDIDATES
from candidate_executor import execute_candidate
from independent_evaluator import evaluate
from ground_truth import GROUND_TRUTH


def main():
    print("=== AgentProbe: Independent Evaluator Tests ===")

    passed = 0
    total = 0

    for candidate in ATTACK_CANDIDATES:
        candidate_id = candidate["candidate_id"]

        observation = execute_candidate(candidate)
        result = evaluate(candidate_id, observation)

        expected_class = GROUND_TRUTH[candidate_id][
            "expected_vulnerability_class"
        ]

        expected_control = expected_class is None

        if expected_control:
            success = (
                result["is_safe_control"] is True
                and result["safe_control_passed"] is True
                and result["verified_vulnerability"] is False
                and result["verified_class"] is None
            )
        else:
            success = (
                result["is_safe_control"] is False
                and result["verified_vulnerability"] is True
                and result["verified_class"] == expected_class
                and result["safe_control_passed"] is False
            )

        total += 1

        if success:
            passed += 1

        print()
        print(f"Candidate: {candidate_id}")
        print(f"Expected class: {expected_class}")
        print(f"Is safe control: {result['is_safe_control']}")
        print(f"Verified vulnerability: {result['verified_vulnerability']}")
        print(f"Safe control passed: {result['safe_control_passed']}")
        print(f"Result: {'PASS' if success else 'FAIL'}")

    print()
    print("=== Test Summary ===")
    print(f"Passed: {passed}/{total}")

    if passed != total:
        raise AssertionError(
            f"{total - passed} evaluator tests failed."
        )

    print("All evaluator tests passed!")


if __name__ == "__main__":
    main()

