# SQLite Database MCP Server

This is an implementation of a Database MCP Server using FastMCP and SQLite. It provides tools to search, insert, and aggregate data, along with resources to inspect the database schema.

## Features

- **Tools**:
  - `search`: Safe parameterized search with filters and pagination.
  - `insert`: Insert new rows safely.
  - `aggregate`: Compute metrics like COUNT, AVG, SUM.
- **Resources**:
  - `schema://database`: Full database schema.
  - `schema://table/{table_name}`: Individual table schema.
- **Safety**: Rejects bad table names, columns, and operators. Prevents SQL injection.

## Setup Instructions

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Initialize the database (this will create `database.db` and insert seed data):
   ```bash
   python init_db.py
   ```

## Testing Steps

**Unit Tests:**
Run the test suite using pytest to verify internal logic and validations:
```bash
pytest tests/test_server.py -v
```

**MCP Server Verification:**
Run the verification script to test the server directly via stdio as an MCP client:
```bash
python verify_server.py
```

**MCP Inspector:**
You can use the MCP Inspector to test the UI:
```bash
# On Linux/macOS
./start_inspector.sh

# On Windows
npx -y @modelcontextprotocol/inspector python mcp_server.py
```

## Client Configuration Example

### Gemini CLI
```bash
gemini mcp add sqlite-lab python /ABSOLUTE/PATH/TO/implementation/mcp_server.py --description "SQLite lab FastMCP server" --timeout 10000
```

### Claude Code
Add this to your `.mcp.json`:
```json
{
  "mcpServers": {
    "sqlite-lab": {
      "type": "stdio",
      "command": "python",
      "args": ["/ABSOLUTE/PATH/TO/implementation/mcp_server.py"],
      "env": {}
    }
  }
}
```
