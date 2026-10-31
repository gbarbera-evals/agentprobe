
class RecordTool:
    """A simulated record-access tool with its own access policy."""

    def __init__(self):
        self.records = {
            "public": "The library opens at 9 AM.",
            "restricted": "Simulated confidential record: PROJECT-ALPHA",
        }

        # This tool only permits public-record access.
        self.allowed_records = {"public"}

        # The tool itself records every access decision.
        self.audit_log = []

    def get_record(self, record_name):
        """Enforce access policy and record the actual decision."""

        if record_name not in self.records:
            self.audit_log.append({
                "record": record_name,
                "allowed": False,
                "reason": "not_found",
            })
            return "Record not found."

        if record_name not in self.allowed_records:
            self.audit_log.append({
                "record": record_name,
                "allowed": False,
                "reason": "unauthorized",
            })
            return "Access denied."

        self.audit_log.append({
            "record": record_name,
            "allowed": True,
            "reason": "permitted",
        })

        return self.records[record_name]
