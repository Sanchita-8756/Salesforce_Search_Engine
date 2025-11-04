# Salesforce MCP Frontend & Backend

A simple web interface for interacting with Salesforce through the MCP (Model Context Protocol) server.

## Architecture

- **Frontend**: Simple HTML/CSS/JavaScript interface for Salesforce operations
- **Backend**: FastAPI server that bridges frontend requests to Salesforce MCP server
- **MCP Server**: Salesforce agent server exposing Salesforce operations as MCP tools

## Features

### Frontend Interface
- **SOQL Queries**: Execute Salesforce Object Query Language statements
- **Record Operations**: Get, create, update records
- **Object Metadata**: Describe Salesforce objects and their fields
- **Real-time Results**: JSON formatted responses displayed in the UI

### Backend API
- `POST /query` - Execute SOQL queries and data retrieval operations
- `POST /action` - Create, update, delete Salesforce records  
- `GET /health` - Health check endpoint

## Setup

1. **Install Dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Configure Salesforce Credentials**:
   Create `.env` file in the root directory:
   ```
   SF_USERNAME=your_salesforce_username
   SF_PASSWORD=your_salesforce_password
   SF_SECURITY_TOKEN=your_security_token
   SF_DOMAIN=login  # or test for sandbox
   ```

3. **Start the Application**:
   ```bash
   python start_app.py
   ```
   
   This will:
   - Start the FastAPI backend on port 8000
   - Start the frontend server on port 3000
   - Open your browser automatically

## Usage Examples

### SOQL Query
```sql
SELECT Id, Name, Type FROM Account LIMIT 10
```

### Get Record
- Object: `Account`
- Record ID: `0011234567890ABC`

### Create Record
- Object: `Account`
- Data: `{"Name": "Test Account", "Type": "Customer"}`

### Update Record
- Object: `Account` 
- Record ID: `0011234567890ABC`
- Data: `{"Name": "Updated Account Name"}`

## API Command Format

The backend accepts commands in specific formats:

- **SOQL**: `soql:SELECT Id, Name FROM Account`
- **Get Record**: `get:Account/0011234567890ABC`
- **Create**: `create:Account` (with payload)
- **Update**: `update:Account/0011234567890ABC` (with payload)
- **Delete**: `delete:Account/0011234567890ABC`
- **Describe**: `describe:Account`

## Error Handling

- Invalid SOQL queries return Salesforce error messages
- Missing credentials show connection errors
- Malformed JSON data displays parsing errors
- All errors are displayed in the frontend results panel

## Development

To modify the interface:
1. Edit `frontend/index.html` for UI changes
2. Edit `frontend/script.js` for functionality
3. Edit `frontend/style.css` for styling
4. Edit `backend/main.py` for API changes

The application uses direct Salesforce agent calls as fallback when MCP server is not available.