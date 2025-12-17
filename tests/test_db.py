import psycopg2
import pytest
import json

def test_connection_and_insert():
    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="password",
            host="localhost",
            port=5432
        )
        cur = conn.cursor()
        # Ensure table exists
        cur.execute('''CREATE EXTENSION IF NOT EXISTS vector;''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS code_context (
                id serial PRIMARY KEY,
                content text,
                metadata jsonb,
                embedding vector(768)
            );
        ''')
        # Insert dummy record
        cur.execute("INSERT INTO code_context (content, metadata, embedding) VALUES (%s, %s, %s) RETURNING id;",
                    ("sample", json.dumps({"source": "unit-test"}), [0.0]*768))
        row_id = cur.fetchone()[0]
        assert isinstance(row_id, int)
        # Clean up
        cur.execute("DELETE FROM code_context WHERE id = %s;", (row_id,))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        pytest.fail(f"Test failed with error: {e}")

