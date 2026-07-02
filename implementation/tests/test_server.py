import os
import sys
import json
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# We need to set the environment variable BEFORE importing mcp_server
os.environ["SQLITE_PATH"] = "test_lab.db"

# Now import modules
from init_db import init_sqlite
from mcp_server import search, insert, aggregate, database_schema, table_schema

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    # Initialize a test database
    if os.path.exists("test_lab.db"):
        os.remove("test_lab.db")
    init_sqlite("test_lab.db")
    yield
    # Cleanup after tests
    if os.path.exists("test_lab.db"):
        try:
            os.remove("test_lab.db")
        except PermissionError:
            pass # Windows might hold a lock, ignore for now

def test_search_tool():
    # Call the search tool
    result_str = search(table="students", filters=[{"column": "cohort", "operator": "=", "value": "A1"}])
    assert "Validation Error" not in result_str
    assert "Database Error" not in result_str
    results = json.loads(result_str)
    assert len(results) > 0
    assert results[0]["cohort"] == "A1"

def test_insert_tool():
    result_str = insert(table="courses", values={"title": "Test Course", "credits": 5})
    assert "success" in result_str
    result = json.loads(result_str)
    assert result["inserted"]["title"] == "Test Course"

def test_aggregate_tool():
    result_str = aggregate(table="students", metric="avg", column="score", group_by="cohort")
    assert "Error" not in result_str
    results = json.loads(result_str)
    assert len(results) > 0
    assert "value" in results[0]

def test_database_schema_resource():
    result_str = database_schema()
    assert "Error" not in result_str
    schema = json.loads(result_str)
    assert "students" in schema
    assert "courses" in schema
    assert "enrollments" in schema

def test_table_schema_resource():
    result_str = table_schema("students")
    assert "Error" not in result_str
    schema = json.loads(result_str)
    assert isinstance(schema, list)
    assert any(col["name"] == "name" for col in schema)

def test_invalid_search():
    result_str = search(table="non_existent_table")
    assert "Validation Error" in result_str
