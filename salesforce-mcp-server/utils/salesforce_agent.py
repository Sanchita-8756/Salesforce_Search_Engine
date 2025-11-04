"""High-level agent that exposes operations in a safe, documented way for MCP tools.

This file is where you put domain-specific logic (pagination, batching, field clean-up).
"""

from typing import Any, Dict, List
from .salesforce_client import SalesforceClient


class SalesforceAgent:
    def __init__(self, client: SalesforceClient):
        self.client = client

    # -------------------- Query / Read --------------------
    def run_soql(self, soql: str) -> Dict[str, Any]:
        """Run an arbitrary SOQL statement. Use with caution (avoid injection from untrusted sources)."""
        return self.client.query(soql)

    def get_record(self, object_name: str, record_id: str) -> Dict[str, Any]:
        return self.client.get(object_name, record_id)

    def describe_object(self, object_name: str) -> Dict[str, Any]:
        return self.client.describe_sobject(object_name)

    def list_objects(self) -> Dict[str, Any]:
        return self.client.list_sobjects()

    # -------------------- Write --------------------
    def create_record(self, object_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self.client.create(object_name, payload)

    def update_record(self, object_name: str, record_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self.client.update(object_name, record_id, payload)

    def delete_record(self, object_name: str, record_id: str) -> Dict[str, Any]:
        return self.client.delete(object_name, record_id)

    # -------------------- Helper / pagination example --------------------
    def query_all(self, soql: str) -> List[Dict[str, Any]]:
        """Execute SOQL and follow nextRecordsUrl to gather all records."""
        resp = self.client.query(soql)
        records = resp.get("records", [])
        next_records_url = resp.get("nextRecordsUrl")
        while next_records_url:
            more = self.client._sf.session.get(self.client._sf.base_url + next_records_url)
            more.raise_for_status()
            data = more.json()
            records.extend(data.get("records", []))
            next_records_url = data.get("nextRecordsUrl")
        return records

