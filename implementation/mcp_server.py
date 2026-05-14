import json
from typing import Dict, Any, List, Optional
from fastmcp import FastMCP
from pydantic import BaseModel, Field
import db

mcp = FastMCP("sqlite-lab")

# Pydantic models for tools

class FilterCondition(BaseModel):
    column: str = Field(description="The column name to filter on")
    operator: str = Field(description="The SQL operator (=, <, >, <=, >=, !=, LIKE)", default="=")
    value: Any = Field(description="The value to compare against")

@mcp.tool()
def search(
    table: str, 
    filters: Optional[List[FilterCondition]] = None, 
    order_by: Optional[str] = None, 
    limit: int = 50, 
    offset: int = 0
) -> str:
    """
    Search rows in a table.
    """
    try:
        filter_dicts = [f.dict() for f in filters] if filters else None
        results = db.search(table, filters=filter_dicts, order_by=order_by, limit=limit, offset=offset)
        return json.dumps(results, indent=2)
    except db.DatabaseError as e:
        return f"Error: {e}"
    except Exception as e:
        return f"Unexpected Error: {e}"

@mcp.tool()
def insert(table: str, data: Dict[str, Any]) -> str:
    """
    Insert a new row into a table.
    data must be a dictionary mapping column names to values.
    """
    try:
        result = db.insert(table, data)
        return json.dumps(result, indent=2)
    except db.DatabaseError as e:
        return f"Error: {e}"
    except Exception as e:
        return f"Unexpected Error: {e}"

@mcp.tool()
def aggregate(table: str, agg_func: str, column: str = "*", group_by: Optional[str] = None) -> str:
    """
    Compute an aggregate metric on a table.
    agg_func: COUNT, AVG, SUM, MIN, MAX
    column: column name to aggregate
    group_by: column name to group by
    """
    try:
        results = db.aggregate(table, agg_func, column, group_by)
        return json.dumps(results, indent=2)
    except db.DatabaseError as e:
        return f"Error: {e}"
    except Exception as e:
        return f"Unexpected Error: {e}"

@mcp.resource("schema://database")
def get_full_schema() -> str:
    """Get the full database schema."""
    try:
        schema = db.get_db_schema()
        return json.dumps(schema, indent=2)
    except Exception as e:
        return f"Error: {e}"

@mcp.resource("schema://table/{table_name}")
def get_table_schema(table_name: str) -> str:
    """Get the schema for a specific table."""
    try:
        schema = db.get_table_schema(table_name)
        return json.dumps(schema, indent=2)
    except db.DatabaseError as e:
        return f"Error: {e}"
    except Exception as e:
        return f"Unexpected Error: {e}"

if __name__ == "__main__":
    mcp.run(transport='stdio')
