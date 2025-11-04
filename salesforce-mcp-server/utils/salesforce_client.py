"""Lightweight Salesforce client wrapper using simple_salesforce.

This wrapper centralizes connection handling and exposes helper methods:
- query(soql)
- get(object_name, record_id)
- create(object_name, payload)
- update(object_name, record_id, payload)
- delete(object_name, record_id)
- describe_sobject(object_name)
- list_sobjects()

If you prefer OAuth2 flows or JWT, extend this class to implement token refresh.
"""

import os
from typing import Any, Dict, Optional
from simple_salesforce import Salesforce, SalesforceMalformedRequest
from dotenv import load_dotenv

load_dotenv()


class SalesforceClient:
    def __init__(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        security_token: Optional[str] = None,
        domain: Optional[str] = None,
        instance_url: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
    ):
        username = username or os.environ.get("SF_USERNAME")
        password = password or os.environ.get("SF_PASSWORD")
        security_token = security_token or os.environ.get("SF_SECURITY_TOKEN")
        domain = domain or os.environ.get("SF_DOMAIN") or "login"
        instance_url = instance_url or os.environ.get("SF_INSTANCE_URL")

        self._sf = Salesforce(
            username=username,
            password=password,
            security_token=security_token,
            domain=domain,
            instance_url=instance_url,
        )

    def query(self, soql: str) -> Dict[str, Any]:
        """Execute a SOQL query and return the result dict from simple_salesforce."""
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

