from flask import Flask
import psycopg2

app = Flask(__name__)

DB_CONFIG = {
    'host': 'db',
    'database': 'statuspage',
    'user': 'appuser',
    'password': 'SecurePass123!'
}

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

@app.route('/')
def index():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT 1;')
        db_status = "Connected successfully!"
        cur.close()
        conn.close()
    except Exception as e:
        db_status = f"Database connection failed: {str(e)}"
    
    return f"<h1>Status Page</h1><p>DB Status: {db_status}</p>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
