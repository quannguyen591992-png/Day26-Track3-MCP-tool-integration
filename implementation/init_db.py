import sqlite3
import os

SQLITE_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    cohort TEXT NOT NULL,
    score REAL
);

CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    credits INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS enrollments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY(student_id) REFERENCES students(id),
    FOREIGN KEY(course_id) REFERENCES courses(id)
);
"""

PG_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS students (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    cohort TEXT NOT NULL,
    score REAL
);

CREATE TABLE IF NOT EXISTS courses (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    credits INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS enrollments (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(id),
    course_id INTEGER NOT NULL REFERENCES courses(id),
    status TEXT NOT NULL
);
"""

SEED_STUDENTS = [
    ('Alice', 'A1', 95.0),
    ('Bob', 'A1', 82.5),
    ('Charlie', 'B2', 88.0),
    ('Diana', 'A1', 91.0)
]

SEED_COURSES = [
    ('Introduction to MCP', 3),
    ('Advanced SQLite', 4),
    ('Database Security', 3)
]

SEED_ENROLLMENTS = [
    (1, 1, 'active'),
    (2, 1, 'active'),
    (1, 2, 'completed'),
    (3, 3, 'active')
]

def init_sqlite(db_path="lab.db"):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.executescript(SQLITE_SCHEMA_SQL)
    
    # Check if empty before seeding
    cur.execute("SELECT COUNT(*) FROM students")
    if cur.fetchone()[0] == 0:
        cur.executemany("INSERT INTO students (name, cohort, score) VALUES (?, ?, ?)", SEED_STUDENTS)
        cur.executemany("INSERT INTO courses (title, credits) VALUES (?, ?)", SEED_COURSES)
        cur.executemany("INSERT INTO enrollments (student_id, course_id, status) VALUES (?, ?, ?)", SEED_ENROLLMENTS)
    
    conn.commit()
    conn.close()
    print(f"SQLite database initialized at {db_path}")

def init_postgres(dsn):
    try:
        import psycopg2
        conn = psycopg2.connect(dsn)
        cur = conn.cursor()
        cur.execute(PG_SCHEMA_SQL)
        
        cur.execute("SELECT COUNT(*) FROM students")
        if cur.fetchone()[0] == 0:
            cur.executemany("INSERT INTO students (name, cohort, score) VALUES (%s, %s, %s)", SEED_STUDENTS)
            cur.executemany("INSERT INTO courses (title, credits) VALUES (%s, %s)", SEED_COURSES)
            cur.executemany("INSERT INTO enrollments (student_id, course_id, status) VALUES (%s, %s, %s)", SEED_ENROLLMENTS)
        
        conn.commit()
        conn.close()
        print("PostgreSQL database initialized")
    except ImportError:
        print("psycopg2 is not installed, cannot initialize PostgreSQL.")
    except Exception as e:
        print(f"Error initializing PostgreSQL: {e}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default="sqlite", choices=["sqlite", "postgres"])
    parser.add_argument("--path", default="lab.db", help="SQLite database path")
    parser.add_argument("--dsn", default="", help="PostgreSQL DSN")
    args = parser.parse_args()
    
    if args.db == "sqlite":
        init_sqlite(args.path)
    else:
        init_postgres(args.dsn)
