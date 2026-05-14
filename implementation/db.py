import sqlite3
import os
from typing import Dict, Any, List, Optional, Tuple
from contextlib import closing

DB_PATH = os.path.join(os.path.dirname(__file__), 'database.db')

ALLOWED_TABLES = {'students', 'courses', 'enrollments'}
ALLOWED_OPERATORS = {'=', '<', '>', '<=', '>=', '!=', 'LIKE'}
ALLOWED_AGG_FUNCS = {'COUNT', 'AVG', 'SUM', 'MIN', 'MAX'}

class DatabaseError(Exception):
    pass

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_db_schema() -> Dict[str, List[Dict[str, str]]]:
    """Return the schema for all allowed tables."""
    schema = {}
    for table in ALLOWED_TABLES:
        schema[table] = get_table_schema(table)
    return schema

def get_table_schema(table_name: str) -> List[Dict[str, str]]:
    """Return the schema for a specific table."""
    if table_name not in ALLOWED_TABLES:
        raise DatabaseError(f"Table '{table_name}' is not allowed or does not exist.")
    
    with closing(get_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        return [
            {
                "name": col["name"],
                "type": col["type"],
                "notnull": bool(col["notnull"]),
                "pk": bool(col["pk"])
            }
            for col in columns
        ]

def _validate_table(table_name: str):
    if table_name not in ALLOWED_TABLES:
        raise DatabaseError(f"Invalid table name: {table_name}")

def _validate_columns(table_name: str, columns: List[str]):
    schema = get_table_schema(table_name)
    valid_cols = {col["name"] for col in schema}
    for col in columns:
        if col != "*" and col not in valid_cols:
            raise DatabaseError(f"Invalid column '{col}' for table '{table_name}'")

def search(table: str, filters: Optional[List[Dict[str, Any]]] = None, order_by: Optional[str] = None, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
    """
    Search rows in a table.
    filters: [{"column": "age", "operator": ">", "value": 18}]
    """
    _validate_table(table)
    
    query = f"SELECT * FROM {table}"
    params = []
    
    if filters:
        conditions = []
        for f in filters:
            col = f.get("column")
            op = f.get("operator", "=").upper()
            val = f.get("value")
            
            _validate_columns(table, [col])
            
            if op not in ALLOWED_OPERATORS:
                raise DatabaseError(f"Invalid operator: {op}")
            
            conditions.append(f"{col} {op} ?")
            params.append(val)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
            
    if order_by:
        # order_by could be "column ASC" or "column DESC"
        parts = order_by.split()
        if len(parts) > 2:
            raise DatabaseError(f"Invalid order_by clause: {order_by}")
        col = parts[0]
        direction = parts[1].upper() if len(parts) == 2 else "ASC"
        if direction not in ("ASC", "DESC"):
            raise DatabaseError(f"Invalid sort direction: {direction}")
        
        _validate_columns(table, [col])
        query += f" ORDER BY {col} {direction}"
        
    query += " LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    with closing(get_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def insert(table: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Insert a new row."""
    if not data:
        raise DatabaseError("Insert data cannot be empty.")
    
    _validate_table(table)
    _validate_columns(table, list(data.keys()))
    
    columns = list(data.keys())
    placeholders = ", ".join(["?"] * len(columns))
    col_str = ", ".join(columns)
    
    query = f"INSERT INTO {table} ({col_str}) VALUES ({placeholders}) RETURNING *"
    params = list(data.values())
    
    with closing(get_connection()) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            row = cursor.fetchone()
            conn.commit()
            return dict(row) if row else {}
        except sqlite3.IntegrityError as e:
            raise DatabaseError(f"Integrity error: {e}")

def aggregate(table: str, agg_func: str, column: str = "*", group_by: Optional[str] = None) -> List[Dict[str, Any]]:
    """Aggregate data."""
    _validate_table(table)
    
    agg_func = agg_func.upper()
    if agg_func not in ALLOWED_AGG_FUNCS:
        raise DatabaseError(f"Invalid aggregate function: {agg_func}")
        
    _validate_columns(table, [column])
    
    select_clause = f"{agg_func}({column}) as result"
    if group_by:
        _validate_columns(table, [group_by])
        select_clause = f"{group_by}, {select_clause}"
        
    query = f"SELECT {select_clause} FROM {table}"
    
    if group_by:
        query += f" GROUP BY {group_by}"
        
    with closing(get_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
