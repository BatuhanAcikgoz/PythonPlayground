# migrations/add_language_field.py
"""
Safe migration script to add `language` column to programming_question table
if it doesn't exist. This script uses SQLAlchemy Engine directly and is safe to
run multiple times (it checks existence first).

Usage: python migrations/add_language_field.py
"""
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import SQLAlchemyError
import sys
import os

# Ensure project root is on sys.path so imports like `from config import Config` work
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    # Import config dynamically from project
    from config import Config
except Exception:
    # If importing config fails, try to adjust PYTHONPATH
    print('Could not import Config from config.py', file=sys.stderr)
    raise


def main():
    db_uri = Config().SQLALCHEMY_DATABASE_URI
    print(f'Using database URI: {db_uri}')

    engine = create_engine(db_uri)
    inspector = inspect(engine)

    table_name = 'programming_question'
    col_name = 'language'

    try:
        if table_name not in inspector.get_table_names():
            print(f"Table '{table_name}' does not exist. Exiting.")
            return

        cols = [c['name'] for c in inspector.get_columns(table_name)]
        if col_name in cols:
            print(f"Column '{col_name}' already exists on '{table_name}'. Nothing to do.")
            return

        # Add column with default 'python' and not null
        alter_sql = text(f"ALTER TABLE {table_name} ADD COLUMN {col_name} VARCHAR(20) NOT NULL DEFAULT 'python';")
        with engine.connect() as conn:
            print(f"Adding column '{col_name}' to table '{table_name}'...")
            conn.execute(alter_sql)
            conn.commit()
        print('Migration applied successfully.')

    except SQLAlchemyError as e:
        print('SQLAlchemyError while applying migration:', str(e), file=sys.stderr)
        raise


if __name__ == '__main__':
    main()
