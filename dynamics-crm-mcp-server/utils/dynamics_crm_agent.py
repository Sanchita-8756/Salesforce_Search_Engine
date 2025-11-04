"""High-level agent that exposes operations in a safe, documented way for MCP tools.

This file is where you put domain-specific logic (pagination, batching, field clean-up).
"""

from typing import Any, Dict, List
from .dynamics_crm_client import DynamicsCrmClient


class DynamicsCrmAgent:
    def __init__(self, client: DynamicsCrmClient):
        self.client = client

    # -------------------- Query / Read --------------------
    def run_odata_query(self, odata_query: str) -> Dict[str, Any]:
        """Run an arbitrary OData query. Use with caution (avoid injection from untrusted sources)."""
        return self.client.query(odata_query)

    def get_record(self, entity_name: str, record_id: str) -> Dict[str, Any]:
        """Get a single record by ID."""
        return self.client.get(entity_name, record_id)

    def get_entity_metadata(self, entity_name: str) -> Dict[str, Any]:
        """Get metadata for a specific entity."""
        return self.client.get_entity_metadata(entity_name)

    def list_entities(self) -> Dict[str, Any]:
        """List all available entities."""
        return self.client.list_entities()

    # -------------------- Write --------------------
    def create_record(self, entity_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new record."""
        return self.client.create(entity_name, payload)

    def update_record(self, entity_name: str, record_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing record."""
        return self.client.update(entity_name, record_id, payload)

    def delete_record(self, entity_name: str, record_id: str) -> Dict[str, Any]:
        """Delete a record."""
        return self.client.delete(entity_name, record_id)

    # -------------------- Helper / pagination example --------------------
    def query_all(self, odata_query: str) -> List[Dict[str, Any]]:
        """Execute OData query and follow @odata.nextLink to gather all records."""
        resp = self.client.query(odata_query)
        records = resp.get("value", [])
        next_link = resp.get("@odata.nextLink")
        
        while next_link:
            # Extract the query part from the next link
            next_query = next_link.split("/api/data/v9.2/")[-1]
            more = self.client.query(next_query)
            records.extend(more.get("value", []))
            next_link = more.get("@odata.nextLink")
            
        return records

    # -------------------- Common CRM Operations --------------------
    def get_contacts(self, filter_query: str = None) -> List[Dict[str, Any]]:
        """Get contacts with optional filter."""
        query = "contacts"
        if filter_query:
            query += f"?$filter={filter_query}"
        return self.query_all(query)

    def get_accounts(self, filter_query: str = None) -> List[Dict[str, Any]]:
        """Get accounts with optional filter."""
        query = "accounts"
        if filter_query:
            query += f"?$filter={filter_query}"
        return self.query_all(query)

    def get_opportunities(self, filter_query: str = None) -> List[Dict[str, Any]]:
        """Get opportunities with optional filter."""
        query = "opportunities"
        if filter_query:
            query += f"?$filter={filter_query}"
        return self.query_all(query)

    def get_leads(self, filter_query: str = None) -> List[Dict[str, Any]]:
        """Get leads with optional filter."""
        query = "leads"
        if filter_query:
            query += f"?$filter={filter_query}"
        return self.query_all(query)