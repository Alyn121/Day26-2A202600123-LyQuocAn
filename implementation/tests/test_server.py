import pytest
import sqlite3
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import db
import init_db
from mcp_server import search, insert, aggregate, get_full_schema, get_table_schema

@pytest.fixture(autouse=True)
def setup_database():
    init_db.init_db()
    yield

def test_db_search():
    # Valid search
    res = db.search('students', limit=2)
    assert len(res) == 2
    
    # Filter search (=)
    res = db.search('students', filters=[{"column": "cohort", "operator": "=", "value": "A1"}])
    assert len(res) == 3

    # Filter search (>)
    res = db.search('students', filters=[{"column": "age", "operator": ">", "value": 20}])
    assert len(res) == 3 # Bob (22), Charlie (21), Diana (23)

    # Filter search (LIKE)
    res = db.search('courses', filters=[{"column": "title", "operator": "LIKE", "value": "%101%"}])
    assert len(res) == 2 # Math 101, History 101

    # Order by DESC
    res = db.search('students', order_by="age DESC")
    assert res[0]['age'] == 23 # Diana
    assert res[-1]['age'] == 19 # Eve

    # Pagination (limit and offset)
    res = db.search('students', order_by="id ASC", limit=2, offset=2)
    assert len(res) == 2
    assert res[0]['name'] == 'Charlie'

    # Invalid table
    with pytest.raises(db.DatabaseError):
        db.search('invalid_table')
        
    # Invalid column
    with pytest.raises(db.DatabaseError):
        db.search('students', filters=[{"column": "invalid_col", "operator": "=", "value": "A1"}])

    # Invalid operator
    with pytest.raises(db.DatabaseError):
        db.search('students', filters=[{"column": "cohort", "operator": "DROP TABLE", "value": "A1"}])

    # Invalid order by clause
    with pytest.raises(db.DatabaseError):
        db.search('students', order_by="age DESC DROP TABLE")

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
    # COUNT
    res = db.aggregate('students', 'COUNT', '*')
    assert res[0]["result"] == 5
    
    # AVG
    res = db.aggregate('students', 'AVG', 'age')
    assert res[0]["result"] == 21.0

    # GROUP BY
    res = db.aggregate('students', 'COUNT', '*', group_by='cohort')
    # Should return rows: A1 -> 3, B2 -> 2
    # The output format is [{"cohort": "A1", "result": 3}, ...]
    cohort_map = {row["cohort"]: row["result"] for row in res}
    assert cohort_map["A1"] == 3
    assert cohort_map["B2"] == 2

    # Invalid func
    with pytest.raises(db.DatabaseError):
        db.aggregate('students', 'INVALID_FUNC', '*')
        
    # Invalid group by
    with pytest.raises(db.DatabaseError):
        db.aggregate('students', 'COUNT', '*', group_by='invalid_col')

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
