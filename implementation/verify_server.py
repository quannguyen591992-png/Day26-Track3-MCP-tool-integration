import sys
import json
from db import SQLiteAdapter, ValidationError

def run_tests():
    print("Setting up test database adapter...")
    adapter = SQLiteAdapter("lab.db")
    
    print("\n1. Testing list_tables()")
    tables = adapter.list_tables()
    print("Tables found:", tables)
    assert "students" in tables
    assert "courses" in tables
    
    print("\n2. Testing get_table_schema('students')")
    schema = adapter.get_table_schema("students")
    print(json.dumps(schema, indent=2))
    assert any(col["name"] == "name" for col in schema)
    
    print("\n3. Testing search (All students in cohort A1)")
    results = adapter.search("students", filters=[{"column": "cohort", "operator": "=", "value": "A1"}])
    print(json.dumps(results, indent=2))
    assert len(results) > 0
    
    print("\n4. Testing insert (New student)")
    new_student = {"name": "Test User", "cohort": "C3", "score": 100.0}
    inserted = adapter.insert("students", new_student)
    print("Inserted:", inserted)
    assert inserted["name"] == "Test User"
    
    print("\n5. Testing aggregate (Average score by cohort)")
    agg = adapter.aggregate("students", "avg", column="score", group_by="cohort")
    print(json.dumps(agg, indent=2))
    assert len(agg) > 0
    
    print("\n6. Testing validation (Invalid table)")
    try:
        adapter.search("hacker_table")
        print("FAIL: Should have rejected invalid table.")
        sys.exit(1)
    except ValidationError as e:
        print("Success: Caught validation error:", e)

    print("\nAll DB logic tests passed!")
    print("To test the FastMCP server, run: npx -y @modelcontextprotocol/inspector python implementation/mcp_server.py")

if __name__ == "__main__":
    run_tests()
