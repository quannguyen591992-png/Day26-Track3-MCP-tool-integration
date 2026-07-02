import os
import json
import argparse
from fastmcp import FastMCP
from db import SQLiteAdapter, PostgresAdapter, ValidationError

# Initialize adapter based on environment
DB_TYPE = os.environ.get("DB_TYPE", "sqlite")
if DB_TYPE == "postgres":
    DSN = os.environ.get("DATABASE_URL", "postgresql://user:password@localhost/dbname")
    adapter = PostgresAdapter(DSN)
else:
    DB_PATH = os.environ.get("SQLITE_PATH", "lab.db")
    adapter = SQLiteAdapter(DB_PATH)

mcp = FastMCP("SQLite Lab MCP Server")

@mcp.tool()
def search(table: str, columns: list[str] = None, filters: list[dict] = None, limit: int = 20, offset: int = 0, order_by: str = None, descending: bool = False) -> str:
    """Search for records in a database table. filters is a list of dicts with 'column', 'operator', and 'value'."""
    try:
        results = adapter.search(table, columns, filters, limit, offset, order_by, descending)
        return json.dumps(results, default=str)
    except ValidationError as e:
        return f"Validation Error: {e}"
    except Exception as e:
        return f"Database Error: {e}"

@mcp.tool()
def insert(table: str, values: dict) -> str:
    """Insert a new record into a table. values is a dictionary mapping column names to values."""
    try:
        result = adapter.insert(table, values)
        return json.dumps({"status": "success", "inserted": result}, default=str)
    except ValidationError as e:
        return f"Validation Error: {e}"
    except Exception as e:
        return f"Database Error: {e}"

@mcp.tool()
def aggregate(table: str, metric: str, column: str = None, filters: list[dict] = None, group_by: str = None) -> str:
    """Compute an aggregate metric (count, avg, sum, min, max) on a table."""
    try:
        results = adapter.aggregate(table, metric, column, filters, group_by)
        return json.dumps(results, default=str)
    except ValidationError as e:
        return f"Validation Error: {e}"
    except Exception as e:
        return f"Database Error: {e}"

@mcp.resource("schema://database")
def database_schema() -> str:
    """Get the full schema of the database."""
    try:
        tables = adapter.list_tables()
        schema = {}
        for t in tables:
            schema[t] = adapter.get_table_schema(t)
        return json.dumps(schema, indent=2)
    except Exception as e:
        return f"Error reading schema: {e}"

@mcp.resource("schema://table/{table_name}")
def table_schema(table_name: str) -> str:
    """Get the schema of a specific table."""
    try:
        schema = adapter.get_table_schema(table_name)
        return json.dumps(schema, indent=2)
    except ValidationError as e:
        return f"Validation Error: {e}"
    except Exception as e:
        return f"Error reading schema: {e}"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--transport", default="stdio", choices=["stdio", "sse"])
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--auth-token", help="Require this token for SSE auth (Bearer)", default="")
    args = parser.parse_args()

    if args.transport == "sse" and args.auth_token:
        # FastMCP uses FastAPI under the hood for SSE in most Python implementations.
        # This is a basic way to add auth middleware if the app is exposed.
        try:
            from starlette.middleware.base import BaseHTTPMiddleware
            from starlette.responses import JSONResponse

            class AuthMiddleware(BaseHTTPMiddleware):
                async def dispatch(self, request, call_next):
                    auth_header = request.headers.get("Authorization")
                    if auth_header != f"Bearer {args.auth_token}":
                        return JSONResponse({"detail": "Unauthorized"}, status_code=401)
                    return await call_next(request)

            # Try to add middleware if mcp object has the internal fastapi app
            if hasattr(mcp, '_app'):
                mcp._app.add_middleware(AuthMiddleware)
            elif hasattr(mcp, 'app'):
                mcp.app.add_middleware(AuthMiddleware)
            else:
                print("Warning: Could not attach AuthMiddleware to FastMCP app.")
        except ImportError:
            print("Warning: starlette is not installed, cannot attach auth middleware.")

    if args.transport == "sse":
        mcp.run(transport="sse", port=args.port)
    else:
        mcp.run()
