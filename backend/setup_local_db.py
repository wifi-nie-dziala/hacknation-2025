"""Setup local database for development."""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'hacknation')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')

def setup_database():
    print("Setting up database...")

    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()

        print(f"Connected to database {DB_NAME}")

        init_sql_path = '../database/init.sql' if os.path.exists('../database/init.sql') else '/database/init.sql'
        with open(init_sql_path, 'r') as f:
            sql = f.read()

        print("Executing init.sql...")
        cur.execute(sql)

        print("Database setup complete!")
        print("\nDummy data created:")
        print("- Job 11111111-1111-1111-1111-111111111111 (pending)")
        print("- Job 22222222-2222-2222-2222-222222222222 (processing)")
        print("- Job 33333333-3333-3333-3333-333333333333 (completed)")
        print("- Job 44444444-4444-4444-4444-444444444444 (failed)")

        cur.close()
        conn.close()

    except psycopg2.OperationalError as e:
        print(f"Error connecting to database: {e}")
        print("\nMake sure PostgreSQL is running and accessible.")
        print(f"Connection details: host={DB_HOST}, port={DB_PORT}, database={DB_NAME}, user={DB_USER}")
        return False
    except Exception as e:
        print(f"Error setting up database: {e}")
        return False

    return True

if __name__ == '__main__':
    setup_database()

