"""Simple Salesforce client for backend use."""

import os
from typing import Any, Dict, Optional
from simple_salesforce import Salesforce, SalesforceMalformedRequest
from dotenv import load_dotenv

load_dotenv()

class SalesforceClient:
    def __init__(self):
        username = os.environ.get("SF_USERNAME")
        password = os.environ.get("SF_PASSWORD")
        security_token = os.environ.get("SF_SECURITY_TOKEN")
        domain = os.environ.get("SF_DOMAIN", "login")
        
        if not all([username, password, security_token]):
            raise ValueError("Missing Salesforce credentials. Check SF_USERNAME, SF_PASSWORD, SF_SECURITY_TOKEN in .env")
        
        self._sf = Salesforce(
            username=username,
            password=password,
            security_token=security_token,
            domain=domain,
        )

    def query(self, soql: str) -> Dict[str, Any]:
        try:
            return self._sf.query(soql)
        except SalesforceMalformedRequest as e:
            raise RuntimeError(f"SOQL query failed: {e}")

    def get(self, object_name: str, record_id: str) -> Dict[str, Any]:
        return self._sf.__getattr__(object_name).get(record_id)

    def create(self, object_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._sf.__getattr__(object_name).create(payload)

    def update(self, object_name: str, record_id: str, payload: Dict[str, Any]) -> dict:
        return self._sf.__getattr__(object_name).update(record_id, payload)

    def delete(self, object_name: str, record_id: str) -> dict:
        return self._sf.__getattr__(object_name).delete(record_id)

    def describe_sobject(self, object_name: str) -> Dict[str, Any]:
        return self._sf.__getattr__(object_name).describe()

    def list_sobjects(self) -> Dict[str, Any]:
        return self._sf.describe()