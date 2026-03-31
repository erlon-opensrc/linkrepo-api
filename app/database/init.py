from .config import create_table_and_database

def init_db() -> None:
    create_table_and_database()
    print('Database initialized successfully!')
