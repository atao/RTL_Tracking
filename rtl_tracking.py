import fileinput
import sqlite3
import json
import sys


class Database:
    def __init__(self, db_name):
        self.db_name = db_name if db_name.endswith(".db") else f"{db_name}.db"
        self._conn = None

    def connect(self):
        """Opens a single persistent connection and sets performance pragmas."""
        if not self._conn:
            self._conn = sqlite3.connect(self.db_name)
            # Crucial optimization tweaks for SD cards / Raspberry Pi storage
            self._conn.execute("PRAGMA journal_mode = WAL;")
            self._conn.execute("PRAGMA synchronous = NORMAL;")
        return self._conn

    def close(self):
        """Safely closes the persistent connection."""
        if self._conn:
            self._conn.close()
            self._conn = None

    def prepare_database(self, table, columns):
        """Creates the target table dynamically if it does not exist."""
        try:
            conn = self.connect()
            cursor = conn.cursor()
            columns_definitions = ', '.join([f'"{col}" {dtype}' for col, dtype in columns.items()])
            query = f'CREATE TABLE IF NOT EXISTS "{table}" ({columns_definitions})'
            cursor.execute(query)
            conn.commit()
            print(f"[+] Table '{table}' in '{self.db_name}' successfully verified/created!")
        except sqlite3.Error as e:
            print(f"[-] Database schema error: {e}", file=sys.stderr)
            raise e

    def create_view(self, view_name, select_query):
        """Creates a virtual analytics view configuration."""
        try:
            conn = self.connect()
            cursor = conn.cursor()
            query = f'CREATE VIEW IF NOT EXISTS "{view_name}" AS {select_query}'
            cursor.execute(query)
            conn.commit()
            print(f"[+] View '{view_name}' successfully verified/created!")
        except sqlite3.Error as e:
            print(f"[-] View creation error: {e}", file=sys.stderr)
            raise e

    def store_data(self, table, data):
        """Inserts dataset values into the target table using the active connection profile."""
        last_id = None
        try:
            conn = self.connect()
            cursor = conn.cursor()
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['?'] * len(data))
            query = f'INSERT OR IGNORE INTO "{table}" ({columns}) VALUES ({placeholders})'
            
            cursor.execute(query, tuple(data.values()))
            last_id = cursor.lastrowid
            conn.commit()
            return last_id
        except sqlite3.IntegrityError:
            print(f"[!] Record already exists inside table '{table}'")
        except sqlite3.Error as e:
            print(f"[-] Runtime insertion tracking error: {e}", file=sys.stderr)
        finally:
            # Prevents local NameError unassigned local variable crashes
            if last_id is not None:
                print(f"[+] Inserted row ID: {last_id} - Data: {data}")


# Define the aggregated analysis view query
view_query = '''
SELECT model, id, COUNT(*) as count
FROM data
GROUP BY id
ORDER BY model
'''

# Initialize implementation environment
json2db = Database("data.db")
json2db.prepare_database('data', {'time': 'TEXT', 'model': 'TEXT', 'id': 'TEXT'})
json2db.create_view('tracking', view_query)

print("[+] Listening for live streaming logs pipeline input... (Press Ctrl+C to exit)")

try:
    # Read the data stream (from stdin / piped commands) line by line
    for line in fileinput.input():
        if not line.strip():
            continue
        try:
            d = json.loads(line)
            # Safely verify structural key configurations exist prior to query mapping
            if all(k in d for k in ('time', 'model', 'id')):
                json2db.store_data("data", {
                    'time': d['time'], 
                    'model': d['model'], 
                    'id': d['id']
                })
        except json.JSONDecodeError:
            # Silently skip malformed pipeline text injections
            pass
        except Exception as e:
            print(f"[!] Processing loop anomaly: {e}", file=sys.stderr)

except KeyboardInterrupt:
    print("\n[-] Interrupted by user. Shutting down data synchronization...")
finally:
    # Explicitly shutdown connection channels safely
    json2db.close()
    print("[+] Database resource released successfully.")
