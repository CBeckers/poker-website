from flask import Flask, jsonify
from flask_cors import CORS
import mysql.connector
from flask_socketio import SocketIO
import time
import os
import threading
from decimal import Decimal  # Import the Decimal class
from datetime import datetime # Import datetime class
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
socketio = SocketIO(app, cors_allowed_origins="*")

# Database configuration
db_config = {
    'host': os.environ.get('MYSQL_HOST'),
    'user': os.environ.get('MYSQL_USER'),
    'password': os.environ.get('MYSQL_PASSWORD'),
    'database': os.environ.get('MYSQL_DATABASE')
}

def fetch_data():
    try:
        db = mysql.connector.connect(**db_config)
        cursor = db.cursor(dictionary=True)
        query = "SELECT * FROM sensor_data"
        cursor.execute(query)
        results = cursor.fetchall()
        print("Raw Results", results)

        # Convert Decimal objects to float AND datetime objects to string
        for row in results:
            for key, value in row.items():
                if isinstance(value, Decimal):
                    row[key] = float(value)
                    print(f"Converted key '{key}' for value {value} into type {type(value)}")
                elif isinstance(value, datetime):
                    row[key] = value.isoformat()  # Convert to ISO string
                    print(f"Converted key '{key}' for value {value} into type string")

        print("JSON-safe results: ", results) # check
        return results

    except mysql.connector.Error as err:
        print(f"Error: '{err}'")
        return None

    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'db' in locals() and db:
            db.close()

@app.route('/api/initial_data')
def get_initial_data():
    data = fetch_data()
    if data:
        return jsonify(data)
    else:
        return jsonify({'error': 'Failed to fetch data'}), 500

@socketio.on('connect')
def handle_connect():
    print('Client connected')

def send_data_update():
    data = fetch_data()
    if data:
        socketio.emit('data_update', data)

def trigger_data_update():
    send_data_update()

# Function to monitor the database and trigger updates
def monitor_database_changes():
  last_known_max_id = 0 # Track the highest ID to detect changes

  while True:
    try:
      # Connect to the database inside the loop to handle potential disconnections
      db = mysql.connector.connect(**db_config)
      cursor = db.cursor()

      # Query the database to find the maximum ID
      cursor.execute("SELECT MAX(id) FROM sensor_data")
      max_id = cursor.fetchone()[0]  # Fetch the result

      if max_id is None:
        max_id = 0

      # Check if a new row has been added (ID is higher than before)
      if max_id > last_known_max_id:
        print("New data detected in the database!")
        trigger_data_update()
        last_known_max_id = max_id # Update what we know

      # Cleanup
      cursor.close()
      db.close()

      time.sleep(0.1)  # Check every 2 seconds (adjust as needed)
    except mysql.connector.Error as e:
      print(f"Database error: {e}")
    except Exception as e:
      print(f"General error: {e}")
    finally:
      if 'cursor' in locals() and cursor:
        cursor.close()
      if 'db' in locals() and db:
        db.close()

# Start the monitoring thread
monitor_thread = threading.Thread(target=monitor_database_changes)
monitor_thread.daemon = True
monitor_thread.start()

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)


