import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2.extras import register_json, Json
import sys

def create_table():
    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="password",
            host="localhost",
            port=5432
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()

        # Enable pgvector extension
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")

        # Create table with the necessary columns
        cur.execute('''
            CREATE TABLE IF NOT EXISTS code_context (
                id serial PRIMARY KEY,
                content text,
                metadata jsonb,
                embedding vector(768)
            );
        ''')

        print("Table 'code_context' created or already exists.")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    create_table()

