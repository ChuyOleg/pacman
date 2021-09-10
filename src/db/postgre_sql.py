import psycopg2
from psycopg2 import OperationalError


def create_connection(db_name, db_user, db_password, db_host, db_port):
    connection = None
    try:
        connection = psycopg2.connect(
            database=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port
        )
        print("Connected to postgreSQL")
    except OperationalError as e:
        print(f"The error '{e}' occurred")
    return connection


def execute_query_postgreSQL(connection, query):
    connection.autocommit = True
    cursor = connection.cursor()
    try:
        result = cursor.execute(query)
        return result
    except OperationalError as e:
        print(f"The Error '{e}' occurred")


create_table_query = """
CREATE TABLE IF NOT EXISTS game_stat (    
    id SERIAL PRIMARY KEY,
    score int,
    time_seconds int,
    search_type varchar(64) DEFAULT Null
)    
"""

pgSQL_db = create_connection(
    "pacman", "postgres", "postgreSQL", "127.0.0.1", "5432"
)


def load_data_to_db(data):
    execute_query_postgreSQL(pgSQL_db, f"INSERT INTO game_stat(score, time_seconds, search_type)"
                                       f" VALUES({data[0]}, {data[1]}, '{data[2]}')")


execute_query_postgreSQL(pgSQL_db, create_table_query)
