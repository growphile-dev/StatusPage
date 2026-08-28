from flask import Flask, render_template_string
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

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>System Status</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
        body { background-color: #0f172a; color: #f8fafc; display: flex; justify-content: center; align-items: center; min-height: 100vh; padding: 20px; }
        .card { background: #1e293b; border: 1px solid #334155; border-radius: 16px; padding: 32px; width: 100%; max-width: 480px; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5); }
        .header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 24px; padding-bottom: 16px; border-bottom: 1px solid #334155; }
        .title { font-size: 1.25rem; font-weight: 600; color: #f8fafc; }
        .status-row { display: flex; align-items: center; justify-content: space-between; padding: 16px; background: #0f172a; border-radius: 10px; margin-top: 12px; }
        .service-name { font-size: 0.95rem; font-weight: 500; color: #94a3b8; }
        .status-badge { display: flex; align-items: center; gap: 8px; font-size: 0.875rem; font-weight: 600; }
        .dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; }
        
        .operational { color: #34d399; }
        .operational .dot { background-color: #10b981; box-shadow: 0 0 10px #10b981; animation: pulse 2s infinite; }
        
        .degraded { color: #f87171; }
        .degraded .dot { background-color: #ef4444; box-shadow: 0 0 10px #ef4444; }

        @keyframes pulse {
            0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
            70% { transform: scale(1); box-shadow: 0 0 0 8px rgba(16, 185, 129, 0); }
            100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
        }
    </style>
</head>
<body>
    <div class="card">
        <div class="header">
            <span class="title">System Status</span>
            <span style="font-size: 0.8rem; color: #64748b;">Live Overview</span>
        </div>
        
        <div class="status-row">
            <span class="service-name">Web Application</span>
            <div class="status-badge operational">
                <span class="dot"></span> Operational
            </div>
        </div>

        <div class="status-row">
            <span class="service-name">PostgreSQL Database</span>
            {% if db_connected %}
            <div class="status-badge operational">
                <span class="dot"></span> Operational
            </div>
            {% else %}
            <div class="status-badge degraded">
                <span class="dot"></span> Disconnected
            </div>
            {% endif %}
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    db_connected = False
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT 1;')
        cur.close()
        conn.close()
        db_connected = True
    except Exception:
        db_connected = False
    
    return render_template_string(HTML_TEMPLATE, db_connected=db_connected)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
