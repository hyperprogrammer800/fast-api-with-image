import psycopg2, os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_USER = os.getenv('MONGO_USER')
MONGO_PASS = os.getenv('MONGO_PASS')
POSTGRES_PASS = os.getenv('POSTGRES_PASS')

def get_connection(): 
    try: 
        conn = psycopg2.connect(host="localhost",
                                dbname="postgres", 
                                user="postgres",
                                password=POSTGRES_PASS, 
                                port=5432)
        cur = conn.cursor()
        return conn, cur
    except: 
        return {'error' : 'Postgres conection failed'}

def get_db_table():
    try:
        client = MongoClient(f"mongodb+srv://hyperprogrammer800:flaskapi123@cluster0.0mrqopb.mongodb.net/?retryWrites=true&w=majority")
        db = client.production
        table = db.images 
        return table
    except:
        return {'error' : 'Mongodb conection failed'}


def create_table(connection, table_name):
    try:
        cur = connection.cursor()
        cur.execute(f"""CREATE TABLE IF NOT EXISTS {table_name} (
                            id SERIAL PRIMARY KEY,
                            fullname VARCHAR(50) NOT NULL,
                            email VARCHAR(50) NOT NULL,
                            password VARCHAR(255),
                            phone INT
                    );
                    """)

        connection.commit()

        # cur.close()
        # connection.close()
        return cur
    except:
        return False
    
def check_exist(cur,table_name, email, phone):
    cur.execute(f"""
                SELECT COUNT(*) FROM {table_name} WHERE email = '{email}' OR phone = {phone}
                """)
    return cur.fetchone()[0]

def get_users(cur, table_name, user_id=None):
    user_str = f"WHERE id = {user_id}" if user_id else ""
    cur.execute(f""" SELECT * FROM {table_name} {user_str}
                """)
    return cur.fetchone()

def insert_row(conn, cur, table_name, user_dict):
    try:
        cur.execute(f""" INSERT INTO {table_name} (fullname, email, password, phone) 
                        VALUES {tuple(user_dict.values())} RETURNING id""")
        data = cur.fetchone() 
        print("User ID of latest entry:", data[0], data) 
        conn.commit()
        cur.close()
        conn.close()
        return data[0]
    except:
        return {"error" : "Insert user data error"}
