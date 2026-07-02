class ValidationError(Exception):
    """Raised when a request cannot be safely executed."""


class SQLiteAdapter:
    """
    Pseudocode responsibilities:
    - open SQLite connections
    - list tables
    - inspect schemas
    - execute search queries
    - execute inserts
    - execute aggregates
    - validate identifiers before building SQL
    """

    def connect(self):
        # return sqlite connection with row_factory enabled
        pass

    def list_tables(self):
        # query sqlite_master and return non-internal tables
        pass

    def get_table_schema(self, table):
        # run PRAGMA table_info(table) and normalize result
        pass

    def search(self, table, columns=None, filters=None, limit=20, offset=0, order_by=None, descending=False):
        """
        Pseudocode:
        - validate identifiers
        - build WHERE clause from supported operators
        - build ORDER BY if requested
        - append LIMIT and OFFSET
        - execute with bound parameters
        """
        pass

    def insert(self, table, values):
        """
        Pseudocode:
        - validate table and columns
        - build INSERT statement with placeholders
        - commit transaction
        - return inserted payload
        """
        pass

    def aggregate(self, table, metric, column=None, filters=None, group_by=None):
        """
        Pseudocode:
        - validate metric
        - validate identifiers
        - build SELECT metric(column) AS value
        - optionally add GROUP BY
        - execute and return rows
        """
        pass
