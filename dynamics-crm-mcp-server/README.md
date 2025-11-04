# Dynamics CRM MCP Server

A Model Context Protocol (MCP) server for Microsoft Dynamics CRM integration, built in the same format as the Salesforce MCP server.

## Features

- **OData Query Support**: Execute arbitrary OData queries against Dynamics CRM
- **CRUD Operations**: Create, read, update, and delete records
- **Entity Management**: Get metadata and list available entities
- **Common CRM Operations**: Specialized methods for contacts, accounts, opportunities, and leads
- **Authentication**: Supports both OAuth2 and basic authentication
- **Pagination**: Automatic handling of large result sets

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables or update `config/config.yaml.example`:

### OAuth2 Authentication (Recommended)
```bash
export CRM_SERVER_URL="https://yourorg.crm.dynamics.com"
export CRM_CLIENT_ID="your-client-id"
export CRM_CLIENT_SECRET="your-client-secret"
export CRM_TENANT_ID="your-tenant-id"
```

### Basic Authentication (On-premise)
```bash
export CRM_SERVER_URL="https://yourcrm.company.com"
export CRM_USERNAME="your-username"
export CRM_PASSWORD="your-password"
export CRM_DOMAIN="your-domain"
```

3. Run the server:
```bash
python mcp_servers/dynamics_crm_agent_server.py
```

The server will start on `http://localhost:8003/sse`

## Available Tools

### Query Operations
- `run_odata_query(odata_query)` - Execute arbitrary OData queries
- `query_all(odata_query)` - Execute query with automatic pagination
- `get_record(entity_name, record_id)` - Get single record by ID

### CRUD Operations
- `create_record(entity_name, payload)` - Create new record
- `update_record(entity_name, record_id, payload)` - Update existing record
- `delete_record(entity_name, record_id)` - Delete record

### Metadata Operations
- `get_entity_metadata(entity_name)` - Get entity schema information
- `list_entities()` - List all available entities

### Common CRM Operations
- `get_contacts(filter_query?)` - Get contacts with optional filter
- `get_accounts(filter_query?)` - Get accounts with optional filter
- `get_opportunities(filter_query?)` - Get opportunities with optional filter
- `get_leads(filter_query?)` - Get leads with optional filter

## Usage Examples

### Query Contacts
```python
# Get all contacts
get_contacts()

# Get contacts with filter
get_contacts("statecode eq 0")
```

### Create Account
```python
create_record("accounts", {
    "name": "Contoso Ltd",
    "telephone1": "555-0123",
    "websiteurl": "https://contoso.com"
})
```

### Run OData Query
```python
run_odata_query("contacts?$select=fullname,emailaddress1&$top=10")
```

## Configuration

The server uses the same configuration format as the Salesforce MCP server:

```yaml
settings:
  dynamics_crm:
    server_url: ${CRM_SERVER_URL}
    username: ${CRM_USERNAME}
    password: ${CRM_PASSWORD}
    domain: ${CRM_DOMAIN}
    client_id: ${CRM_CLIENT_ID}
    client_secret: ${CRM_CLIENT_SECRET}
    tenant_id: ${CRM_TENANT_ID}

server:
  host: ${HOST}
  port: ${PORT}
  debug: ${DEBUG}

mcp:
  name: ${MCP_NAME}
```