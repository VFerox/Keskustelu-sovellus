import os
import sqlite3

def init_db():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    db_path = os.path.join(current_dir, "database.db")
    
    schema_path = os.path.join(current_dir, "schema.sql")
    
    print(f"Looking for schema.sql at: {schema_path}")
    print(f"Creating database at: {db_path}")


    try:
        os.remove(db_path)
        print("Removed old database file")
    except OSError:
        print("No old database file to remove")

    print("Creating new database...")
    connection = sqlite3.connect(db_path)

    connection.execute("PRAGMA foreign_keys = ON")

    try:
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
            print("Read schema.sql successfully")
            connection.executescript(schema_sql)
            connection.commit()
            print("Executed schema successfully")
    except FileNotFoundError:
        print(f"ERROR: Could not find schema.sql at {schema_path}")
        return
    except Exception as e:
        print(f"ERROR: Failed to create database: {str(e)}")
        return
    finally:
        connection.close()
        print("Database connection closed")

if __name__ == "__main__":
    init_db()
    print("Database initialization complete!")
