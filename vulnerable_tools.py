
class VulnerableRecordTool:
    """A deliberately vulnerable tool for local security experiments.

    WARNING: This tool intentionally fails to enforce access permissions.
    Use only with the fictional records in this project.
    """

    def __init__(self):
        self.records = {
            "public": "The library opens at 9 AM.",
            "restricted": "Simulated confidential record: PROJECT-ALPHA",
        }

        # The tool claims only public records are permitted.
        self.allowed_records = {"public"}

        # This log records what the tool reports.
        self.audit_log = []

    def get_record(self, record_name):
        """Intentionally flawed: returns records without checking permissions."""

        if record_name not in self.records:
            self.audit_log.append({
                "record": record_name,
                "allowed": False,
                "reason": "not_found",
            })
            return "Record not found."

        # VULNERABILITY: permission is never checked here.
        self.audit_log.append({
            "record": record_name,
            "allowed": record_name in self.allowed_records,
            "reason": (
                "permitted"
                if record_name in self.allowed_records
                else "unauthorized"
            ),
        })

        # BUG: returns restricted content even when access is unauthorized.
        return self.records[record_name]
