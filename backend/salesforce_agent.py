"""Simple Salesforce agent for backend use."""

from typing import Any, Dict, List
from .salesforce_client import SalesforceClient

class SalesforceAgent:
    def __init__(self, client: SalesforceClient):
        self.client = client

    def run_soql(self, soql: str) -> Dict[str, Any]:
        return self.client.query(soql)

    def get_record(self, object_name: str, record_id: str) -> Dict[str, Any]:
        return self.client.get(object_name, record_id)

    def describe_object(self, object_name: str) -> Dict[str, Any]:
        return self.client.describe_sobject(object_name)

    def list_objects(self) -> Dict[str, Any]:
        return self.client.list_sobjects()

    def create_record(self, object_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self.client.create(object_name, payload)

    def update_record(self, object_name: str, record_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self.client.update(object_name, record_id, payload)

    def delete_record(self, object_name: str, record_id: str) -> Dict[str, Any]:
        return self.client.delete(object_name, record_id)