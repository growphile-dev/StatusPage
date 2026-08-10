from flask import Flask, render_template_string
import psycopg2
import requests
import datetime

app = Flask(__name__)

# Database config
DB_CONFIG = {
    'host': 'db',
    'database': 'statuspage',
    'user': 'appuser',
    'password': 'SecurePass123!'
}

# Services to monitor
SERVICES = [
    {'name': 'Google', 'url': 'https://google.com'},
    {'name': 'GitHub', 'url': 'https://github.com'},
    {'name': 'Cloudflare', 'url': 'https://cloudflare.com'},
    {'name': 'MiniCorp API', 'url': 'http://localhost:5000/health'}
]

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS checks (
            id SERIAL PRIMARY KEY,
            service_name VARCHAR(100),
            url VARCHAR(255),
            status VARCHAR(20),
            response_time_ms INTEGER,
            checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

def check_service(service):
    try:
        start = datetime.datetime.now()
        response = requests.get(service['url'], timeout=10, allow_redirects=True)
        end = datetime.datetime.now()
        response_time = int((end - start).total_seconds() * 1000)
        
        status = 'UP' if response.status_code == 200 else 'DOWN'
        return {
            'name': service['name'],
            'url': service['url'],
            'status': status,
            'response_time': response_time,
            'status_code': response.status_code
        }
    except Exception as e:
        return {
            'name': service['name'],
            'url': service['url'],
            'status': 'DOWN',
            'response_time': 0,
            'status_code': 0
        }

def save_check(result):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO checks (service_name, url, status, response_time_ms)
        VALUES (%s, %s, %s, %s)
    ''', (result['name'], result['url'], result['status'], result['response_time']))
    conn.commit()
    cur.close()
    conn.close()

def get_latest_checks():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        SELECT DISTINCT ON (service_name) 
            service_name, url, status, response_time_ms, checked_at
        FROM checks
        ORDER BY service_name, checked_at DESC
    ''')
    rows = cur.fetchall()
    cur.close()
    conn.close()
    
    checks = []
    for row in rows:
        checks.append({
            'name': row[0],
            'url': row[1],
            'status': row[2],
            'response_time': row[3],
            'checked_at': row[4].strftime('%Y-%m-%d %H:%M:%S')
        })
    return checks

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>StatusPage - Service Monitoring</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        h1 { color: #333; text-align: center; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; max-width: 1200px; margin: 0 auto; }
        .card { background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .card.up { border-left: 5px solid #27ae60; }
        .card.down { border-left: 5px solid #e74c3c; }
        .status { font-size: 24px; font-weight: bold; }
        .status.up { color: #27ae60; }
        .status.down { color: #e74c3c; }
        .url { color: #666; font-size: 14px; margin: 10px 0; }
        .meta { color: #999; font-size: 12px; }
        .refresh { text-align: center; margin-top: 20px; }
        .refresh a { color: #2980b9; text-decoration: none; }
    </style>
</head>
<body>
    <h1>StatusPage</h1>
    <p style="text-align:center; color:#666;">Real-time service monitoring dashboard</p>
    <div class="grid">
        {% for check in checks %}
        <div class="card {{ check.status.lower() }}">
            <div class="status {{ check.status.lower() }}">{{ check.status }}</div>
            <h3>{{ check.name }}</h3>
            <div class="url">{{ check.url }}</div>
            <div class="meta">Response time: {{ check.response_time }}ms</div>
            <div class="meta">Checked: {{ check.checked_at }}</div>
        </div>
        {% endfor %}
    </div>
    <div class="refresh">
        <a href="/">Refresh</a> | <a href="/api/check">Run Check Now</a>
    </div>
</body>
</html>
'''

@app.route('/')
def dashboard():
    checks = get_latest_checks()
    return render_template_string(HTML_TEMPLATE, checks=checks)

@app.route('/api/check')
def run_check():
    results = []
    for service in SERVICES:
        result = check_service(service)
        save_check(result)
        results.append(result)
    return {'checked': len(results), 'results': results}

@app.route('/api/services')
def list_services():
    return {'services': SERVICES}

@app.route('/health')
def health():
    return {'status': 'healthy', 'service': 'StatusPage'}

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
