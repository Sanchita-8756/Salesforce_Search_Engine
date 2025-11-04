"""Lightweight Dynamics CRM client wrapper using requests and ADAL.

This wrapper centralizes connection handling and exposes helper methods:
- query(fetchxml)
- get(entity_name, record_id)
- create(entity_name, payload)
- update(entity_name, record_id, payload)
- delete(entity_name, record_id)
- get_entity_metadata(entity_name)
- list_entities()

Supports both OAuth2 and username/password authentication.
"""

import os
import requests
from typing import Any, Dict, Optional
from urllib.parse import urljoin
from dotenv import load_dotenv

load_dotenv()


class DynamicsCrmClient:
    def __init__(
        self,
        server_url: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        domain: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        tenant_id: Optional[str] = None,
    ):
        self.server_url = server_url or os.environ.get("CRM_SERVER_URL")
        self.username = username or os.environ.get("CRM_USERNAME")
        self.password = password or os.environ.get("CRM_PASSWORD")
        self.domain = domain or os.environ.get("CRM_DOMAIN")
        self.client_id = client_id or os.environ.get("CRM_CLIENT_ID")
        self.client_secret = client_secret or os.environ.get("CRM_CLIENT_SECRET")
        self.tenant_id = tenant_id or os.environ.get("CRM_TENANT_ID")
        
        if not self.server_url:
            raise ValueError("CRM server URL is required")
        
        self.api_url = urljoin(self.server_url, "/api/data/v9.2/")
        self.session = requests.Session()
        self._authenticate()

    def _authenticate(self):
        """Authenticate with Dynamics CRM using OAuth2 or basic auth."""
        if self.client_id and self.client_secret and self.tenant_id:
            self._oauth_authenticate()
        elif self.username and self.password:
            self._basic_authenticate()
        else:
            raise ValueError("Either OAuth2 credentials or username/password required")

    def _oauth_authenticate(self):
        """OAuth2 authentication flow."""
        token_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        
        # Clean server URL for scope
        clean_url = self.server_url.rstrip('/')
        
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'scope': f"{clean_url}/.default"
        }
        
        print(f"Token URL: {token_url}")
        print(f"Scope: {data['scope']}")
        
        response = requests.post(token_url, data=data)
        
        if response.status_code != 200:
            print(f"OAuth Error: {response.status_code}")
            print(f"Response: {response.text}")
        
        response.raise_for_status()
        
        token_data = response.json()
        access_token = token_data['access_token']
        
        self.session.headers.update({
            'Authorization': f'Bearer {access_token}',
            'OData-MaxVersion': '4.0',
            'OData-Version': '4.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json; charset=utf-8'
        })

    def _basic_authenticate(self):
        """Basic authentication (for on-premise deployments)."""
        if self.domain:
            auth_user = f"{self.domain}\\{self.username}"
        else:
            auth_user = self.username
            
        self.session.auth = (auth_user, self.password)
        self.session.headers.update({
            'OData-MaxVersion': '4.0',
            'OData-Version': '4.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json; charset=utf-8'
        })

    def query(self, odata_query: str) -> Dict[str, Any]:
        """Execute an OData query and return the result."""
        try:
            url = urljoin(self.api_url, odata_query)
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"OData query failed: {e}")

    def get(self, entity_name: str, record_id: str) -> Dict[str, Any]:
        """Get a single record by ID."""
        url = urljoin(self.api_url, f"{entity_name}({record_id})")
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def create(self, entity_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new record."""
        url = urljoin(self.api_url, entity_name)
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        
        # Return the created record ID and location
        location = response.headers.get('OData-EntityId', '')
        record_id = location.split('(')[-1].split(')')[0] if location else None
        
        return {
            'id': record_id,
            'location': location,
            'status_code': response.status_code
        }

    def update(self, entity_name: str, record_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing record."""
        url = urljoin(self.api_url, f"{entity_name}({record_id})")
        response = self.session.patch(url, json=payload)
        response.raise_for_status()
        
        return {
            'id': record_id,
            'status_code': response.status_code
        }

    def delete(self, entity_name: str, record_id: str) -> Dict[str, Any]:
        """Delete a record."""
        url = urljoin(self.api_url, f"{entity_name}({record_id})")
        response = self.session.delete(url)
        response.raise_for_status()
        
        return {
            'id': record_id,
            'status_code': response.status_code
        }

    def get_entity_metadata(self, entity_name: str) -> Dict[str, Any]:
        """Get metadata for a specific entity."""
        url = urljoin(self.api_url, f"$metadata#EntitySets('{entity_name}')")
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def list_entities(self) -> Dict[str, Any]:
        """List all available entities."""
        url = urljoin(self.api_url, "$metadata")
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()