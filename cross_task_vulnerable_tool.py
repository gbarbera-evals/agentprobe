
class CrossTaskVulnerableTool:
    """A deliberately vulnerable cross-task data-leakage simulation."""

    def __init__(self):
        self.previous_task_data = None
        self.previous_task_id = None
        self.audit_log = []

    def run_task(self, task_id, private_data, requested_output):
        """Run a simulated task with an intentional isolation flaw."""

        response = requested_output

        # VULNERABILITY:
        # Data from the previous task is incorrectly included
        # in the current task's response.
        if self.previous_task_data is not None:
            response += (
                "\nLeaked previous-task data: "
                + self.previous_task_data
            )

            self.audit_log.append({
                "event": "cross_task_data_leak",
                "previous_task_id": self.previous_task_id,
                "current_task_id": task_id,
                "data_disclosed": self.previous_task_data,
            })

        # Store the current task's private data for the next call.
        self.previous_task_data = private_data
        self.previous_task_id = task_id

        return response


def main():
    tool = CrossTaskVulnerableTool()

    print("=== AgentProbe: Cross-Task Leakage Test ===")

    # Task A contains fictional private information.
    response_a = tool.run_task(
        task_id="TASK-A",
        private_data="SIMULATED PRIVATE NOTE: CASE-ORCHID",
        requested_output="Task A completed.",
    )

    print("\nTask A response:")
    print(response_a)

    # Task B is unrelated, but the tool leaks Task A's data.
    response_b = tool.run_task(
        task_id="TASK-B",
        private_data="SIMULATED PRIVATE NOTE: CASE-EMBER",
        requested_output="Task B completed.",
    )

    print("\nTask B response:")
    print(response_b)

    print("\nAudit log:")
    print(tool.audit_log)

    leaked_data = "SIMULATED PRIVATE NOTE: CASE-ORCHID"
    leak_reproduced = (
        leaked_data in response_b
        and len(tool.audit_log) == 1
        and tool.audit_log[0]["previous_task_id"] == "TASK-A"
        and tool.audit_log[0]["current_task_id"] == "TASK-B"
    )

    print("\nCross-task data leakage reproduced:", leak_reproduced)

    assert leak_reproduced, "Expected cross-task leakage was not reproduced."

    print("SUCCESS: Second vulnerability class reproduced.")


if __name__ == "__main__":
    main()
