import os
import psycopg2
from dotenv import load_dotenv
from tabulate import tabulate

# Load envinronment variables from .env file.
load_dotenv()                                                  

# DB_USERNAME='win'
# DB_PASSWORD='X0pcAcIuH$8t'
# DB_HOST='situation-room.yellowbrick.io'
# DB_NAME='situation_room_production'
PG_USER = os.environ.get('DB_USERNAME')
PG_PASSWORD = os.environ.get('DB_PASSWORD') 
PG_HOST = os.environ.get('DB_HOST') 
PG_NAME = os.environ.get('DB_NAME') 

# Create connection to postgres
connection = psycopg2.connect(
                        user=PG_USER,
                        password=PG_PASSWORD,
                        host=PG_HOST,
                        dbname=PG_NAME
                        )

cursor = connection.cursor()

query = "select * from ybd_builds where build_number = '8579' limit 2"

cursor.execute(query)
print(cursor.fetchall())