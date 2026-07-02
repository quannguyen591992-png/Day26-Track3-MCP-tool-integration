import abc
import sqlite3

class ValidationError(Exception):
    pass

class BaseAdapter(abc.ABC):
    @abc.abstractmethod
    def list_tables(self):
        pass

    @abc.abstractmethod
    def get_table_schema(self, table):
        pass

    @abc.abstractmethod
    def search(self, table, columns=None, filters=None, limit=20, offset=0, order_by=None, descending=False):
        pass

    @abc.abstractmethod
    def insert(self, table, values):
        pass

    @abc.abstractmethod
    def aggregate(self, table, metric, column=None, filters=None, group_by=None):
        pass


def _validate_identifier(name):
    """Ensure table/column names are safe to interpolate."""
    if not name or not isinstance(name, str):
        raise ValidationError("Identifier must be a non-empty string.")
    if not name.isidentifier():
        raise ValidationError(f"Invalid identifier: {name}")
    return name

def _build_where(filters, param_style="?"):
    """
    filters is a list of dicts: {"column": "...", "operator": "...", "value": "..."}
    param_style: "?" for sqlite, "%s" for postgres
    """
    if not filters:
        return "", []
    
    clauses = []
    params = []
    allowed_ops = {"=", "!=", ">", "<", ">=", "<=", "LIKE"}
    
    for f in filters:
        col = _validate_identifier(f.get("column", ""))
        op = f.get("operator", "").upper()
        if op not in allowed_ops:
            raise ValidationError(f"Unsupported operator: {op}")
        clauses.append(f"{col} {op} {param_style}")
        params.append(f.get("value"))
        
    where_clause = " WHERE " + " AND ".join(clauses)
    return where_clause, params

class SQLiteAdapter(BaseAdapter):
    def __init__(self, db_path="lab.db"):
        self.db_path = db_path

    def _get_conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def list_tables(self):
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            return [row['name'] for row in cur.fetchall()]

    def _validate_table(self, table):
        table = _validate_identifier(table)
        tables = self.list_tables()
        if table not in tables:
            raise ValidationError(f"Unknown table: {table}")
        return table

    def get_table_schema(self, table):
        table = self._validate_table(table)
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute(f"PRAGMA table_info({table})")
            columns = []
            for row in cur.fetchall():
                columns.append({
                    "name": row["name"],
                    "type": row["type"],
                    "notnull": bool(row["notnull"]),
                    "pk": bool(row["pk"])
                })
            return columns

    def _validate_columns(self, table, columns):
        schema = self.get_table_schema(table)
        valid_cols = {col["name"] for col in schema}
        validated = []
        for c in columns:
            c = _validate_identifier(c)
            if c not in valid_cols:
                raise ValidationError(f"Unknown column '{c}' for table '{table}'")
            validated.append(c)
        return validated

    def search(self, table, columns=None, filters=None, limit=20, offset=0, order_by=None, descending=False):
        table = self._validate_table(table)
        if columns:
            columns = self._validate_columns(table, columns)
            cols_str = ", ".join(columns)
        else:
            cols_str = "*"
            
        where_sql, params = _build_where(filters, "?")
        
        sql = f"SELECT {cols_str} FROM {table}{where_sql}"
        
        if order_by:
            order_by = _validate_identifier(order_by)
            self._validate_columns(table, [order_by])
            direction = "DESC" if descending else "ASC"
            sql += f" ORDER BY {order_by} {direction}"
            
        if not isinstance(limit, int) or limit < 0:
            raise ValidationError("Limit must be a non-negative integer.")
        if not isinstance(offset, int) or offset < 0:
            raise ValidationError("Offset must be a non-negative integer.")
            
        sql += f" LIMIT {limit} OFFSET {offset}"
        
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute(sql, params)
            return [dict(row) for row in cur.fetchall()]

    def insert(self, table, values):
        table = self._validate_table(table)
        if not values or not isinstance(values, dict):
            raise ValidationError("Values must be a non-empty dictionary.")
            
        cols = self._validate_columns(table, list(values.keys()))
        vals = [values[c] for c in cols]
        
        cols_str = ", ".join(cols)
        placeholders = ", ".join(["?"] * len(cols))
        
        sql = f"INSERT INTO {table} ({cols_str}) VALUES ({placeholders})"
        
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute(sql, vals)
            new_id = cur.lastrowid
            
            schema = self.get_table_schema(table)
            pk_col = next((c["name"] for c in schema if c["pk"]), None)
            
            if pk_col and new_id:
                cur.execute(f"SELECT * FROM {table} WHERE {pk_col} = ?", (new_id,))
                row = cur.fetchone()
                if row:
                    return dict(row)
            
            result = values.copy()
            if pk_col and new_id:
                result[pk_col] = new_id
            return result

    def aggregate(self, table, metric, column=None, filters=None, group_by=None):
        table = self._validate_table(table)
        allowed_metrics = {"count", "avg", "sum", "min", "max"}
        metric = metric.lower()
        if metric not in allowed_metrics:
            raise ValidationError(f"Unsupported metric: {metric}")
            
        if column:
            column = _validate_identifier(column)
            self._validate_columns(table, [column])
            val_expr = f"{metric.upper()}({column})"
        else:
            if metric == "count":
                val_expr = "COUNT(*)"
            else:
                raise ValidationError(f"Metric '{metric}' requires a column.")
                
        select_expr = f"{val_expr} AS value"
        
        if group_by:
            group_by = _validate_identifier(group_by)
            self._validate_columns(table, [group_by])
            select_expr = f"{group_by}, {select_expr}"
            
        where_sql, params = _build_where(filters, "?")
        
        sql = f"SELECT {select_expr} FROM {table}{where_sql}"
        
        if group_by:
            sql += f" GROUP BY {group_by}"
            
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute(sql, params)
            return [dict(row) for row in cur.fetchall()]


class PostgresAdapter(BaseAdapter):
    def __init__(self, dsn):
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor
        except ImportError:
            raise ValidationError("psycopg2 is required for PostgreSQL support.")
        self.dsn = dsn

    def _get_conn(self):
        import psycopg2
        from psycopg2.extras import RealDictCursor
        conn = psycopg2.connect(self.dsn, cursor_factory=RealDictCursor)
        return conn

    def list_tables(self):
        sql = "SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname != 'pg_catalog' AND schemaname != 'information_schema';"
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                return [row['tablename'] for row in cur.fetchall()]

    def _validate_table(self, table):
        table = _validate_identifier(table)
        tables = self.list_tables()
        if table not in tables:
            raise ValidationError(f"Unknown table: {table}")
        return table

    def get_table_schema(self, table):
        table = self._validate_table(table)
        sql = """
            SELECT column_name, data_type, is_nullable, 
                   (SELECT COUNT(*) FROM information_schema.key_column_usage kcu 
                    JOIN information_schema.table_constraints tc ON kcu.constraint_name = tc.constraint_name 
                    WHERE tc.table_name = c.table_name AND kcu.column_name = c.column_name AND tc.constraint_type = 'PRIMARY KEY') > 0 as is_pk
            FROM information_schema.columns c
            WHERE table_name = %s;
        """
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (table,))
                columns = []
                for row in cur.fetchall():
                    columns.append({
                        "name": row["column_name"],
                        "type": row["data_type"],
                        "notnull": row["is_nullable"] == "NO",
                        "pk": row["is_pk"]
                    })
                return columns

    def _validate_columns(self, table, columns):
        schema = self.get_table_schema(table)
        valid_cols = {col["name"] for col in schema}
        validated = []
        for c in columns:
            c = _validate_identifier(c)
            if c not in valid_cols:
                raise ValidationError(f"Unknown column '{c}' for table '{table}'")
            validated.append(c)
        return validated

    def search(self, table, columns=None, filters=None, limit=20, offset=0, order_by=None, descending=False):
        table = self._validate_table(table)
        if columns:
            columns = self._validate_columns(table, columns)
            cols_str = ", ".join(columns)
        else:
            cols_str = "*"
            
        where_sql, params = _build_where(filters, "%s")
        
        sql = f"SELECT {cols_str} FROM {table}{where_sql}"
        
        if order_by:
            order_by = _validate_identifier(order_by)
            self._validate_columns(table, [order_by])
            direction = "DESC" if descending else "ASC"
            sql += f" ORDER BY {order_by} {direction}"
            
        if not isinstance(limit, int) or limit < 0:
            raise ValidationError("Limit must be a non-negative integer.")
        if not isinstance(offset, int) or offset < 0:
            raise ValidationError("Offset must be a non-negative integer.")
            
        sql += f" LIMIT {limit} OFFSET {offset}"
        
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                return [dict(row) for row in cur.fetchall()]

    def insert(self, table, values):
        table = self._validate_table(table)
        if not values or not isinstance(values, dict):
            raise ValidationError("Values must be a non-empty dictionary.")
            
        cols = self._validate_columns(table, list(values.keys()))
        vals = [values[c] for c in cols]
        
        cols_str = ", ".join(cols)
        placeholders = ", ".join(["%s"] * len(cols))
        
        sql = f"INSERT INTO {table} ({cols_str}) VALUES ({placeholders}) RETURNING *"
        
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, vals)
                row = cur.fetchone()
                conn.commit()
                return dict(row) if row else None

    def aggregate(self, table, metric, column=None, filters=None, group_by=None):
        table = self._validate_table(table)
        allowed_metrics = {"count", "avg", "sum", "min", "max"}
        metric = metric.lower()
        if metric not in allowed_metrics:
            raise ValidationError(f"Unsupported metric: {metric}")
            
        if column:
            column = _validate_identifier(column)
            self._validate_columns(table, [column])
            val_expr = f"{metric.upper()}({column})"
        else:
            if metric == "count":
                val_expr = "COUNT(*)"
            else:
                raise ValidationError(f"Metric '{metric}' requires a column.")
                
        select_expr = f"{val_expr} AS value"
        
        if group_by:
            group_by = _validate_identifier(group_by)
            self._validate_columns(table, [group_by])
            select_expr = f"{group_by}, {select_expr}"
            
        where_sql, params = _build_where(filters, "%s")
        
        sql = f"SELECT {select_expr} FROM {table}{where_sql}"
        
        if group_by:
            sql += f" GROUP BY {group_by}"
            
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                return [dict(row) for row in cur.fetchall()]
