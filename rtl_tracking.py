import fileinput
import sqlite3
import json


class database:
    def __init__(self, database):
        self.database = database

    def prepare_database(self, table, columns):
        try:
            conn = sqlite3.connect(self.database)
            cursor = conn.cursor()
            # Dynamically create the column definitions
            columns_definitions = ', '.join([f'"{col}" {dtype}' for col, dtype in columns.items()])
            # Create the SQL query string
            query = f'CREATE TABLE IF NOT EXISTS "{table}" ({columns_definitions})'
            # Execute the query
            cursor.execute(query)
            conn.commit()
            print("[+] {} successfully created!".format(self.database))
        except sqlite3.IntegrityError:
            print("[!] Already exists")
        except Exception as e:
            print(f"[!] Error: {e}")
            conn.rollback()
            raise e
        finally:
            conn.close()

    def create_view(self, view_name, select_query):
        try:
            conn = sqlite3.connect(self.database)
            cursor = conn.cursor()
            query = f'CREATE VIEW IF NOT EXISTS "{view_name}" AS {select_query}'
            cursor.execute(query)
            conn.commit()
            print(f"[+] View {view_name} successfully created!")
        except Exception as e:
            print(f"[!] Error: {e}")
            conn.rollback()
            raise e
        finally:
            conn.close()

    def store_data(self, table, data):
        try:
            conn = sqlite3.connect(self.database)
            cursor = conn.cursor()
            # Dynamically create the column names and placeholders
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['?'] * len(data))
            # Create the SQL query string
            query = f'INSERT OR IGNORE INTO {table} ({columns}) VALUES ({placeholders})'
            # Execute the query with the appropriate values
            cursor.execute(query, tuple(data.values()))
            id = cursor.lastrowid
            conn.commit()
        except sqlite3.IntegrityError:
            print("[!] Already exist")
        except Exception as e:
            print(f"[!] Error {e}")
            conn.rollback()
            raise e
        finally:
            print(f"[+] Last id {id} - {data}")
            conn.close()

# Define the view query
query = '''
SELECT model, id, COUNT(*) as count
FROM data
GROUP BY id
ORDER BY model
'''

json2db = database("data.db")
json2db.prepare_database('data', {'time': 'TEXT', 'model': 'TEXT', 'id': 'TEXT'})
json2db.create_view('tracking', query)

try:
    for line in fileinput.input():
        try:
            d = json.loads(line)
            json2db.store_data("data",
                               {'time': d['time'], 'model': d['model'], 'id': d['id']})
        except:
            pass
except KeyboardInterrupt:
    print("Interrupted by user")
