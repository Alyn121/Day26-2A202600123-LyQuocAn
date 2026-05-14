import pytest
import sqlite3
import os

from implementation import db, init_db
from implementation.mcp_server import search, insert, aggregate, get_full_schema, get_table_schema

@pytest.fixture(autouse=True)
def setup_database():
    init_db.init_db()
    yield

def test_db_search():
    # Valid search
    res = db.search('students', limit=2)
    assert len(res) == 2
    
    # Filter search
    res = db.search('students', filters=[{"column": "cohort", "operator": "=", "value": "A1"}])
    assert len(res) == 3

    # Invalid table
    with pytest.raises(db.DatabaseError):
        db.search('invalid_table')
        
    # Invalid column
    with pytest.raises(db.DatabaseError):
        db.search('students', filters=[{"column": "invalid_col", "operator": "=", "value": "A1"}])

    # Invalid operator
    with pytest.raises(db.DatabaseError):
        db.search('students', filters=[{"column": "cohort", "operator": "DROP TABLE", "value": "A1"}])

def test_db_insert():
    res = db.insert('courses', {"title": "Chemistry 101", "credits": 4})
    assert res["id"] is not None
    assert res["title"] == "Chemistry 101"
    
    # Empty insert
    with pytest.raises(db.DatabaseError):
        db.insert('courses', {})
        
    # Invalid column
    with pytest.raises(db.DatabaseError):
        db.insert('courses', {"invalid_col": "value"})

def test_db_aggregate():
    res = db.aggregate('students', 'COUNT', '*')
    assert res[0]["result"] == 5
    
    # Invalid func
    with pytest.raises(db.DatabaseError):
        db.aggregate('students', 'INVALID_FUNC', '*')

def test_mcp_endpoints():
    # Resource get full schema
    res = get_full_schema()
    assert "students" in res
    assert "courses" in res
    
    # Resource get table schema
    res = get_table_schema("students")
    assert "name" in res
    assert "age" in res
    
    # Invalid table schema
    res = get_table_schema("invalid")
    assert "Error:" in res

    # Tools
    search_res = search("students", limit=1)
    assert "Alice" in search_res
    
    agg_res = aggregate("students", "COUNT")
    assert "5" in agg_res
