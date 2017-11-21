# Import statements
import psycopg2
import psycopg2.extras
from psycopg2 import sql
from config import *
import sys
import csv
db_connection = None
db_cursor = None

# Write code / functions to set up database connection and cursor here.
def get_connection_and_cursor():
    global db_connection, db_cursor
    if not db_connection:
        try:
            db_connection = psycopg2.connect("dbname='{0}' user='{1}' password='{2}'".format(db_name, db_user, db_password))
            print("Success connecting to database")
        except:
            # raise
            print("Unable to connect to the database. Check server and credentials.")
            sys.exit(1) # Stop running program if there's no db connection.

    if not db_cursor:
        db_cursor = db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    return db_connection, db_cursor

# Write code / functions to create tables with the columns you want and all database setup here.
# * **Sites**
#     * ID (SERIAL)
#     * Name (VARCHAR up to 128 chars, UNIQUE)
#     * Type [e.g. "National Lakeshore" or "National Park"] (VARCHAR up to 128 chars)
#     * State_ID (INTEGER - FOREIGN KEY REFERENCING States)
#     * Location (VARCHAR up to 255 chars)
#     * Description (TEXT)
def setup_database():
    conn, cur = get_connection_and_cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS States(
        id SERIAL PRIMARY KEY,
        name VARCHAR(40) NOT NULL UNIQUE)
        """)

    cur.execute("""CREATE TABLE IF NOT EXISTS Sites(
        id SERIAL PRIMARY KEY,
        name VARCHAR(128) NOT NULL UNIQUE,
        type VARCHAR(128),
        state_id INTEGER REFERENCES States(id),
        location VARCHAR(255),
        description TEXT
        )""")
    conn.commit()
def setup_state_table():
    conn, cur = get_connection_and_cursor()


    for state in ('Arkansas', 'California', 'Michigan'):
        cur.execute("""INSERT INTO
            States(name)
            values(%s) ON CONFLICT DO NOTHING """,
            (state,))

    cur.execute(""" select id,name from States """)
    diction = {}
    results = cur.fetchall()
    for a in results:
        id = a["id"]
        state_name = a["name"]
        diction[state_name] = id
    return (diction)



    # cur.execute("""select max(id) from States""")
    # results = cur.fetchall()
    # # print(results)
    # # state_id = results[0]['max']




# Write code / functions to deal with CSV files and insert data into the database here.
def insert(csv_file_name, state_id):

    conn, cur = get_connection_and_cursor()
    # open the file and read
    with open(csv_file_name, 'r') as f:
        csv_reader = csv.DictReader(f)
        for row in csv_reader:
            n = row['NAME']
            t = row['TYPE']
            l = row['LOCATION']
            d = row['DESCRIPTION']
            cur.execute("""INSERT INTO
                Sites(name, type, state_id, location, description)
                values(%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING """,
                (n, t, state_id, l, d))



# Make sure to commit your database changes with .commit() on the database connection.
    conn.commit()


# Write code to be invoked here (e.g. invoking any functions you wrote above)
get_connection_and_cursor()
setup_database()
state_id_map = setup_state_table()
ark_id = state_id_map["Arkansas"]
insert('arkansas.csv', ark_id)
mich_id = state_id_map["Michigan"]
cal_id = state_id_map["California"]
insert('michigan.csv', mich_id)
insert('california.csv', cal_id)

def execute_and_print(query):
    con , cur = get_connection_and_cursor()
    cur.execute(query)
    results = cur.fetchall()
    for r in results:
        print(r)
    print('--> Result Rows:', len(results))
    print()
    
#-------------------
# Write code to make queries and save data in variables here.
# * In Python, query the database for all of the **locations** of the sites.
#(Of course, this data may vary from "Detroit, Michigan" to "Various States:
#AL, AK, AR, OH, CA, NV, MD" or the like. That's OK!) Save the resulting data in a variable called `all_locations`.
all_locations = execute_and_print(""" SELECT "location"  FROM sites """ )
#-------------------
# * In Python, query the database for all of the **names** of the sites whose **descriptions** include the word `beautiful`. Save the resulting data in a variable called `beautiful_sites`.
beautiful_sites = execute_and_print(""" SELECT "name" FROM "sites" WHERE "description" ilike '%beautiful' """)
#-------------------
# * In Python, query the database for the total number of **sites whose type is `National Lakeshore`.
#** Save the resulting data in a variable called `natl_lakeshores`.
natl_lakeshores = execute_and_print (""" SELECT count(*) FROM "sites" WHERE ("type" = 'National Lakeshore')""")
#--------------------
# * In Python, query your database for the **names of all the national sites in Michigan
#**. Save the resulting data in a variable called `michigan_names`. You should use an inner join query to do this.
michigan_names = execute_and_print(""" SELECT "name" FROM "sites" WHERE ("state_id" = 3)""")
#-------------------
# * In Python, query your database for the
#**total number of sites in Arkansas**. Save the resulting data in a variable
# called `total_number_arkansas`. You can use multiple queries + Python code to do this, one subquery, or one inner join query. HINT: You'll need to use an aggregate function!
total_number_arkansas = execute_and_print (""" SELECT count(*) FROM "sites" INNER JOIN "states" ON ("sites"."state_id" = "sites"."state_id") """)
