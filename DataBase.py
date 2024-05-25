import pyodbc
from datetime import datetime
from config import DB_CONFIG

def get_db_connection():
    connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};" \
                        f"SERVER={DB_CONFIG['server']};" \
                        f"DATABASE={DB_CONFIG['database']};" \
                        f"UID={DB_CONFIG['username']};" \
                        f"PWD={DB_CONFIG['password']}"
    return pyodbc.connect(connection_string)

def create_table_if_not_exists():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Users' AND xtype='U')
    CREATE TABLE Users (
        user_id INT PRIMARY KEY,
        name NVARCHAR(100),
        surname NVARCHAR(100),
        address NVARCHAR(255),
        polis_number BIGINT,
        phone_number BIGINT,
        join_date  DATETIME
    )
    """)
    conn.commit()
    conn.close()

def add_user(user_id, name, surname, address, polis_number, phone_number):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO Users (user_id, name, surname, address, polis_number, phone_number, join_date)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (user_id, name, surname, address, polis_number, phone_number, datetime.now()))
    conn.commit()
    conn.close()

def user_exists(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user is not None

# Создаем таблицу при запуске
create_table_if_not_exists()
