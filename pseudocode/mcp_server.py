from fastmcp import FastMCP

# Create the server object.
mcp = FastMCP("SQLite Lab MCP Server")

# Build or load the database adapter here.
# adapter = SQLiteAdapter(...)


@mcp.tool(name="search")
def search(table, filters=None, columns=None, limit=20, offset=0, order_by=None, descending=False):
    """
    Pseudocode:
    1. Validate the table name.
    2. Validate selected columns.
    3. Translate filters into a safe WHERE clause.
    4. Apply ORDER BY, LIMIT, OFFSET if valid.
    5. Execute query through adapter.
    6. Return rows and metadata as structured JSON.
    """


@mcp.tool(name="insert")
def insert(table, values):
    """
    Pseudocode:
    1. Validate table.
    2. Ensure values is not empty.
    3. Validate every column in values.
    4. Execute parameterized INSERT.
    5. Return inserted payload, including generated ID if available.
    """


@mcp.tool(name="aggregate")
def aggregate(table, metric, column=None, filters=None, group_by=None):
    """
    Pseudocode:
    1. Validate metric against allowed functions.
    2. Validate table and column names.
    3. Translate optional filters.
    4. Translate optional GROUP BY.
    5. Execute COUNT / AVG / SUM / MIN / MAX query.
    6. Return aggregate rows.
    """


@mcp.resource("schema://database")
def database_schema():
    """
    Pseudocode:
    1. Inspect all database tables.
    2. Collect column definitions for each table.
    3. Serialize the schema snapshot as JSON text.
    """


@mcp.resource("schema://table/{table_name}")
def table_schema(table_name):
    """
    Pseudocode:
    1. Validate table_name.
    2. Inspect only that table.
    3. Return a JSON description of the table schema.
    """


if __name__ == "__main__":
    # Pseudocode:
    # - parse transport arguments
    # - run stdio by default
    # - optionally run HTTP or SSE transport for demos / bonus work
    mcp.run()
