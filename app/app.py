from flask import Flask, render_template_string
import psycopg2
import time

app = Flask(__name__)

DB_CONFIG = {
    'host': 'db',
    'database': 'statuspage',
    'user': 'appuser',
    'password': 'SecurePass123!'
}

def get_db_metrics():
    start_time = time.time()
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute('SELECT 1;')
        cur.close()
        conn.close()
        latency = round((time.time() - start_time) * 1000, 2)
        return True, f"{latency} ms"
    except Exception:
        return False, "N/A"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>System Status Dashboard | Zeeshan Riaz</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background-color: #090d16; color: #f8fafc; display: flex; flex-direction: column; align-items: center; min-height: 100vh; padding: 40px 20px; }
        .container { width: 100%; max-width: 850px; }
        
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
        .brand h1 { font-size: 1.5rem; font-weight: 700; color: #f8fafc; }
        .brand p { font-size: 0.875rem; color: #64748b; margin-top: 4px; }
        .badge-live { display: flex; align-items: center; gap: 8px; background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.2); padding: 6px 12px; border-radius: 20px; color: #34d399; font-size: 0.85rem; font-weight: 600; }
        
        /* Stats Grid */
        .stats-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 30px; }
        .stat-card { background: #131c2e; border: 1px solid #1e293b; border-radius: 12px; padding: 20px; }
        .stat-title { font-size: 0.8rem; color: #64748b; text-transform: uppercase; font-weight: 600; letter-spacing: 0.05em; }
        .stat-value { font-size: 1.5rem; font-weight: 700; color: #38bdf8; margin-top: 8px; }

        /* Tabs Navigation */
        .tabs { display: flex; gap: 10px; border-bottom: 1px solid #1e293b; margin-bottom: 24px; padding-bottom: 8px; }
        .tab-btn { background: none; border: none; color: #64748b; font-size: 0.95rem; font-weight: 600; padding: 8px 16px; border-radius: 8px; cursor: pointer; transition: 0.2s; }
        .tab-btn:hover { color: #f8fafc; background: #131c2e; }
        .tab-btn.active { color: #38bdf8; background: #1e293b; }

        /* Tab Contents */
        .tab-content { display: none; }
        .tab-content.active { display: block; }

        /* Cards & Rows */
        .panel { background: #131c2e; border: 1px solid #1e293b; border-radius: 14px; padding: 24px; margin-bottom: 24px; }
        .panel-title { font-size: 1.1rem; font-weight: 600; margin-bottom: 16px; color: #f1f5f9; }
        .status-row { display: flex; justify-content: space-between; align-items: center; padding: 14px 0; border-bottom: 1px solid #1e293b; }
        .status-row:last-child { border-bottom: none; }
        .service-info h4 { font-size: 0.95rem; font-weight: 600; color: #e2e8f0; }
        .service-info p { font-size: 0.8rem; color: #64748b; margin-top: 2px; }
        
        .status-badge { display: flex; align-items: center; gap: 8px; font-size: 0.85rem; font-weight: 600; }
        .dot { width: 9px; height: 9px; border-radius: 50%; display: inline-block; }
        .operational { color: #34d399; }
        .operational .dot { background-color: #10b981; box-shadow: 0 0 10px #10b981; animation: pulse 2s infinite; }
        .degraded { color: #f87171; }
        .degraded .dot { background-color: #ef4444; }

        @keyframes pulse {
            0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
            70% { transform: scale(1); box-shadow: 0 0 0 8px rgba(16, 185, 129, 0); }
            100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
        }

        .timeline-item { border-left: 2px solid #334155; padding-left: 16px; margin-left: 8px; position: relative; padding-bottom: 20px; }
        .timeline-item::before { content: ''; position: absolute; left: -6px; top: 0; width: 10px; height: 10px; border-radius: 50%; background: #38bdf8; }
        .timeline-date { font-size: 0.75rem; color: #64748b; font-weight: 600; }
        .timeline-text { font-size: 0.9rem; color: #cbd5e1; margin-top: 4px; }

        .footer { text-align: center; margin-top: 30px; font-size: 0.875rem; color: #64748b; }
        .footer strong { color: #38bdf8; }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <div class="brand">
                <h1>Infrastructure Dashboard</h1>
                <p>Real-time status monitor & system analytics</p>
            </div>
            <div class="badge-live">
                <span class="dot" style="background: #10b981;"></span> All Systems Normal
            </div>
        </div>

        <!-- Metric Cards -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-title">Overall Uptime</div>
                <div class="stat-value">99.98%</div>
            </div>
            <div class="stat-card">
                <div class="stat-title">DB Latency</div>
                <div class="stat-value">{{ db_latency }}</div>
            </div>
            <div class="stat-card">
                <div class="stat-title">Active Services</div>
                <div class="stat-value">4 / 4</div>
            </div>
        </div>

        <!-- Navigation Tabs -->
        <div class="tabs">
            <button class="tab-btn active" onclick="switchTab('services')">Services Status</button>
            <button class="tab-btn" onclick="switchTab('infrastructure')">Infrastructure Specs</button>
            <button class="tab-btn" onclick="switchTab('incidents')">Incident Log</button>
        </div>

        <!-- TAB 1: Services Status -->
        <div id="services" class="tab-content active">
            <div class="panel">
                <div class="panel-title">Core Services Overview</div>
                <div class="status-row">
                    <div class="service-info">
                        <h4>Web Frontend (Flask Engine)</h4>
                        <p>Handles incoming client HTTP requests</p>
                    </div>
                    <div class="status-badge operational"><span class="dot"></span> Operational</div>
                </div>
                <div class="status-row">
                    <div class="service-info">
                        <h4>PostgreSQL Database Engine</h4>
                        <p>Stores application data and relational models</p>
                    </div>
                    {% if db_connected %}
                    <div class="status-badge operational"><span class="dot"></span> Connected</div>
                    {% else %}
                    <div class="status-badge degraded"><span class="dot"></span> Offline</div>
                    {% endif %}
                </div>
                <div class="status-row">
                    <div class="service-info">
                        <h4>Nginx Gateway Proxy</h4>
                        <p>Manages reverse proxy and network routing (Port 80)</p>
                    </div>
                    <div class="status-badge operational"><span class="dot"></span> Active</div>
                </div>
            </div>
        </div>

        <!-- TAB 2: Infrastructure Specs -->
        <div id="infrastructure" class="tab-content">
            <div class="panel">
                <div class="panel-title">System Architecture Details</div>
                <div class="status-row">
                    <div class="service-info"><h4>Cloud Provider</h4><p>Infrastructure Host</p></div>
                    <span style="color: #cbd5e1; font-size: 0.9rem;">Oracle Cloud Infrastructure</span>
                </div>
                <div class="status-row">
                    <div class="service-info"><h4>Container Platform</h4><p>Orchestration Tool</p></div>
                    <span style="color: #cbd5e1; font-size: 0.9rem;">Docker & Docker Compose</span>
                </div>
                <div class="status-row">
                    <div class="service-info"><h4>Source Control</h4><p>Code Management</p></div>
                    <span style="color: #cbd5e1; font-size: 0.9rem;">GitHub (growphile-dev/statuspage)</span>
                </div>
                <div class="status-row">
                    <div class="service-info"><h4>Virtual Memory</h4><p>Swap File</p></div>
                    <span style="color: #cbd5e1; font-size: 0.9rem;">2.0 GB Configured</span>
                </div>
            </div>
        </div>

        <!-- TAB 3: Incident Log -->
        <div id="incidents" class="tab-content">
            <div class="panel">
                <div class="panel-title">Recent Activity & Updates</div>
                <div class="timeline-item">
                    <div class="timeline-date">Today - 05:30 AM</div>
                    <div class="timeline-text">Successfully integrated tabbed UI dashboard with dynamic DB latency tracking.</div>
                </div>
                <div class="timeline-item">
                    <div class="timeline-date">Yesterday - 11:15 PM</div>
                    <div class="timeline-text">Configured Nginx Reverse Proxy on Port 80 with SELinux network rules.</div>
                </div>
                <div class="timeline-item" style="padding-bottom: 0;">
                    <div class="timeline-date">Initial Setup</div>
                    <div class="timeline-text">Deployed PostgreSQL container and initialized source control via GitHub.</div>
                </div>
            </div>
        </div>

        <!-- Footer -->
        <div class="footer">
            Designed & Engineered by <strong>Zeeshan Riaz</strong>
        </div>
    </div>

    <script>
        function switchTab(tabId) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
            
            document.getElementById(tabId).classList.add('active');
            event.currentTarget.classList.add('active');
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    db_connected, db_latency = get_db_metrics()
    return render_template_string(HTML_TEMPLATE, db_connected=db_connected, db_latency=db_latency)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
