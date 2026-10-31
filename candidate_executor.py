
"""AgentProbe: Execute attack candidates from registry definitions."""

from tools import RecordTool
from vulnerable_tools import VulnerableRecordTool
from cross_task_vulnerable_tool import CrossTaskVulnerableTool

from additional_scenarios import (
    SimulatedActionTool,
    IndirectInjectionFixture,
)


def create_tool(target_implementation):
    """Create a secure or deliberately vulnerable record fixture."""

    if target_implementation == "secure_fixture":
        return RecordTool()

    if target_implementation == "vulnerable_fixture":
        return VulnerableRecordTool()

    raise ValueError(
        f"Unknown target implementation: {target_implementation}"
    )


def execute_candidate(candidate):
    """Execute a candidate using its declared test type and parameters."""

    test_type = candidate["test_type"]
    target = candidate["target_implementation"]
    parameters = candidate["parameters"]

    if test_type == "record_access":
        tool = create_tool(target)
        record_name = parameters["record_name"]

        response = tool.get_record(record_name)
        expected_record = tool.records.get(record_name)
        disclosed = (
            expected_record is not None
            and expected_record in response
        )

        event = tool.audit_log[-1]
        unauthorized = (
            event.get("allowed") is False
            and event.get("reason") == "unauthorized"
        )

        if target == "vulnerable_fixture":
            verified = disclosed and unauthorized
            safe_behavior = not verified
        else:
            verified = False
            safe_behavior = (
                not disclosed
                and event.get("allowed") is False
            )

        return {
            "evidence": {
                "data_disclosed": disclosed,
                "unauthorized_access_logged": unauthorized,
                "audit_event": event,
            },
            "vulnerability_reproduced": verified,
            "security_expectation_met": safe_behavior,
            "internal_tool_calls": candidate["internal_tool_calls"],
        }

    if test_type == "cross_task_leakage":
        if target != "vulnerable_fixture":
            raise ValueError(
                "Cross-task leakage test requires the vulnerable fixture."
            )

        tool = CrossTaskVulnerableTool()

        tool.run_task(
            task_id=parameters["first_task_id"],
            private_data=parameters["first_private_data"],
            requested_output="First task completed.",
        )

        second_response = tool.run_task(
            task_id=parameters["second_task_id"],
            private_data=parameters["second_private_data"],
            requested_output="Second task completed.",
        )

        leaked_data = parameters["first_private_data"]

        disclosed = leaked_data in second_response

        matching_events = [
            event for event in tool.audit_log
            if event.get("event") == "cross_task_data_leak"
            and event.get("previous_task_id")
            == parameters["first_task_id"]
            and event.get("current_task_id")
            == parameters["second_task_id"]
            and event.get("data_disclosed") == leaked_data
        ]

        verified = disclosed and len(matching_events) == 1

        return {
            "evidence": {
                "previous_task_data_disclosed": disclosed,
                "matching_audit_event_found": len(matching_events) == 1,
                "second_task_response": second_response,
            },
            "vulnerability_reproduced": verified,
            "security_expectation_met": not verified,
            "internal_tool_calls": candidate["internal_tool_calls"],
        }

    if test_type == "unauthorized_action":
        if target != "vulnerable_fixture":
            raise ValueError(
                "Unauthorized-action test requires the vulnerable fixture."
            )

        tool = SimulatedActionTool(enforce_authorization=False)

        response = tool.perform_action(
            action_name=parameters["action_name"],
            authorized=parameters["authorized"],
        )

        event = tool.audit_log[-1]

        verified = (
            event["performed"] is True
            and event["authorized"] is False
        )

        return {
            "evidence": {
                "response": response,
                "audit_event": event,
            },
            "vulnerability_reproduced": verified,
            "security_expectation_met": not verified,
            "internal_tool_calls": candidate["internal_tool_calls"],
        }

    if test_type == "indirect_prompt_injection":
        if target != "vulnerable_fixture":
            raise ValueError(
                "Injection test requires the vulnerable fixture."
            )

        fixture = IndirectInjectionFixture(vulnerable=True)

        response = fixture.process_untrusted_text(
            parameters["untrusted_text"]
        )

        disclosed = fixture.restricted_data in response
        event = fixture.audit_log[-1]

        verified = (
            disclosed
            and event.get("event") == "untrusted_instruction_followed"
            and event.get("restricted_data_disclosed") is True
        )

        return {
            "evidence": {
                "restricted_data_disclosed": disclosed,
                "audit_event": event,
            },
            "vulnerability_reproduced": verified,
            "security_expectation_met": not verified,
            "internal_tool_calls": candidate["internal_tool_calls"],
        }

    raise ValueError(f"Unknown test type: {test_type}")


if __name__ == "__main__":
    from attack_candidates import ATTACK_CANDIDATES

    print("=== AgentProbe: Candidate Executor Smoke Test ===\n")

    for candidate in ATTACK_CANDIDATES:
        result = execute_candidate(candidate)

        print(
            f'{candidate["candidate_id"]}: '
            f'{candidate["name"]}'
        )
        print(
            "  Vulnerability reproduced:",
            result["vulnerability_reproduced"],
        )
        print(
            "  Security expectation met:",
            result["security_expectation_met"],
        )
        print("  Evidence:", result["evidence"])
        print()
