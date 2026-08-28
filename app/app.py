from flask import Flask, render_template_string
import psycopg2
import time
import os

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
    <title>Enterprise Status | Zeeshan Riaz</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background-color: #070a12; color: #f8fafc; display: flex; flex-direction: column; align-items: center; min-height: 100vh; padding: 40px 20px; }
        .container { width: 100%; max-width: 900px; }
        
        /* Neon Glowing Name Header */
        .creator-header { text-align: center; margin-bottom: 30px; }
        .creator-title { font-size: 0.85rem; letter-spacing: 0.2em; text-transform: uppercase; color: #64748b; font-weight: 700; margin-bottom: 6px; }
        .creator-name { 
            font-size: 2.8rem; 
            font-weight: 900; 
            color: #ffffff;
            text-shadow: 0 0 10px #38bdf8, 0 0 20px #38bdf8, 0 0 40px #0284c7;
            animation: glow-pulse 2.5s infinite alternate;
            letter-spacing: -0.02em;
        }

        @keyframes glow-pulse {
            0% { text-shadow: 0 0 10px #38bdf8, 0 0 20px #38bdf8, 0 0 30px #0284c7; opacity: 0.95; }
            50% { text-shadow: 0 0 15px #818cf8, 0 0 30px #818cf8, 0 0 50px #6366f1; opacity: 1; }
            100% { text-shadow: 0 0 10px #38bdf8, 0 0 25px #38bdf8, 0 0 40px #0284c7; opacity: 0.95; }
        }

        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; background: #0f172a; border: 1px solid #1e293b; padding: 20px 24px; border-radius: 14px; }
        .brand h1 { font-size: 1.25rem; font-weight: 700; color: #f8fafc; }
        .brand p { font-size: 0.85rem; color: #64748b; margin-top: 2px; }
        .badge-live { display: flex; align-items: center; gap: 8px; background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); padding: 6px 14px; border-radius: 20px; color: #34d399; font-size: 0.85rem; font-weight: 600; }
        
        /* Stats Grid */
        .stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 24px; }
        .stat-card { background: #0f172a; border: 1px solid #1e293b; border-radius: 12px; padding: 18px; }
        .stat-title { font-size: 0.75rem; color: #64748b; text-transform: uppercase; font-weight: 700; letter-spacing: 0.05em; }
        .stat-value { font-size: 1.4rem; font-weight: 800; color: #38bdf8; margin-top: 6px; }

        /* Tabs Navigation */
        .tabs { display: flex; gap: 8px; border-bottom: 1px solid #1e293b; margin-bottom: 24px; padding-bottom: 8px; flex-wrap: wrap; }
        .tab-btn { background: none; border: 1px solid transparent; color: #64748b; font-size: 0.9rem; font-weight: 600; padding: 8px 18px; border-radius: 8px; cursor: pointer; transition: 0.2s; }
        .tab-btn:hover { color: #f8fafc; background: #0f172a; }
        .tab-btn.active { color: #38bdf8; background: #0f172a; border-color: #334155; }

        /* Tab Contents */
        .tab-content { display: none; }
        .tab-content.active { display: block; }

        /* Panel & Rows */
        .panel { background: #0f172a; border: 1px solid #1e293b; border-radius: 14px; padding: 24px; margin-bottom: 24px; }
        .panel-title { font-size: 1.05rem; font-weight: 700; margin-bottom: 16px; color: #f1f5f9; display: flex; justify-content: space-between; align-items: center; }
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

        /* Meter bar for live performance */
        .meter-container { width: 140px; background: #1e293b; height: 8px; border-radius: 4px; overflow: hidden; margin-top: 6px; }
        .meter-fill { height: 100%; background: linear-gradient(90deg, #38bdf8, #818cf8); border-radius: 4px; }

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
        <!-- Glowing Creator Header -->
        <div class="creator-header">
            <div class="creator-title">System Designed & Built By</div>
            <div class="creator-name">ZEESHAN RIAZ</div>
        </div>

        <!-- Infrastructure Status Banner -->
        <div class="header">
            <div class="brand">
                <h1>Infrastructure Health Dashboard</h1>
                <p>Live automated monitoring node</p>
            </div>
            <div class="badge-live">
                <span class="dot" style="background: #10b981;"></span> Operational 100%
            </div>
        </div>

        <!-- Metric Cards -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-title">System Uptime</div>
                <div class="stat-value">99.99%</div>
            </div>
            <div class="stat-card">
                <div class="stat-title">DB Latency</div>
                <div class="stat-value">{{ db_latency }}</div>
            </div>
            <div class="stat-card">
                <div class="stat-title">Network Proxy</div>
                <div class="stat-value">Nginx 80</div>
            </div>
            <div class="stat-card">
                <div class="stat-title">Containers</div>
                <div class="stat-value">2 / 2 Online</div>
            </div>
        </div>

        <!-- Navigation Tabs -->
        <div class="tabs">
            <button class="tab-btn active" onclick="switchTab(event, 'services')">Core Services</button>
            <button class="tab-btn" onclick="switchTab(event, 'performance')">Live Performance</button>
            <button class="tab-btn" onclick="switchTab(event, 'infrastructure')">Infrastructure Specs</button>
            <button class="tab-btn" onclick="switchTab(event, 'incidents')">Incident Logs</button>
        </div>

        <!-- TAB 1: Core Services -->
        <div id="services" class="tab-content active">
            <div class="panel">
                <div class="panel-title">Active Platform Services</div>
                <div class="status-row">
                    <div class="service-info">
                        <h4>Python Flask Engine</h4>
                        <p>Core application backend serving REST API</p>
                    </div>
                    <div class="status-badge operational"><span class="dot"></span> Running</div>
                </div>
                <div class="status-row">
                    <div class="service-info">
                        <h4>PostgreSQL Database Engine</h4>
                        <p>Relational SQL database cluster inside Docker</p>
                    </div>
                    {% if db_connected %}
                    <div class="status-badge operational"><span class="dot"></span> Connected</div>
                    {% else %}
                    <div class="status-badge degraded"><span class="dot"></span> Disconnected</div>
                    {% endif %}
                </div>
                <div class="status-row">
                    <div class="service-info">
                        <h4>Nginx Reverse Proxy</h4>
                        <p>High-performance web server & traffic gateway</p>
                    </div>
                    <div class="status-badge operational"><span class="dot"></span> Active</div>
                </div>
            </div>
        </div>

        <!-- TAB 2: Live Performance -->
        <div id="performance" class="tab-content">
            <div class="panel">
                <div class="panel-title">Real-time Performance Metrics</div>
                <div class="status-row">
                    <div class="service-info">
                        <h4>Database Query Response</h4>
                        <p>Round-trip database ping latency</p>
                    </div>
                    <div>
                        <span style="color: #38bdf8; font-weight: 700;">{{ db_latency }}</span>
                        <div class="meter-container"><div class="meter-fill" style="width: 25%;"></div></div>
                    </div>
                </div>
                <div class="status-row">
                    <div class="service-info">
                        <h4>HTTP Server Response Time</h4>
                        <p>Average proxy response latency</p>
                    </div>
                    <div>
                        <span style="color: #34d399; font-weight: 700;">1.8 ms</span>
                        <div class="meter-container"><div class="meter-fill" style="width: 15%; background: #10b981;"></div></div>
                    </div>
                </div>
                <div class="status-row">
                    <div class="service-info">
                        <h4>Container Memory Usage</h4>
                        <p>Allocated RAM across active containers</p>
                    </div>
                    <div>
                        <span style="color: #cbd5e1; font-weight: 700;">148 MB / 1024 MB</span>
                        <div class="meter-container"><div class="meter-fill" style="width: 18%;"></div></div>
                    </div>
                </div>
                <div class="status-row">
                    <div class="service-info">
                        <h4>Docker CPU Load</h4>
                        <p>Overall container CPU utilization</p>
                    </div>
                    <div>
                        <span style="color: #cbd5e1; font-weight: 700;">0.4%</span>
                        <div class="meter-container"><div class="meter-fill" style="width: 5%;"></div></div>
                    </div>
                </div>
            </div>
        </div>

        <!-- TAB 3: Infrastructure Specs -->
        <div id="infrastructure" class="tab-content">
            <div class="panel">
                <div class="panel-title">System Architecture Details</div>
                <div class="status-row">
                    <div class="service-info"><h4>Cloud Provider</h4><p>Host Region</p></div>
                    <span style="color: #cbd5e1; font-size: 0.9rem; font-weight: 600;">Oracle Cloud Infrastructure</span>
                </div>
                <div class="status-row">
                    <div class="service-info"><h4>Container Platform</h4><p>Runtime</p></div>
                    <span style="color: #cbd5e1; font-size: 0.9rem; font-weight: 600;">Docker & Docker Compose</span>
                </div>
                <div class="status-row">
                    <div class="service-info"><h4>Version Control</h4><p>Repository</p></div>
                    <span style="color: #cbd5e1; font-size: 0.9rem; font-weight: 600;">GitHub (growphile-dev/statuspage)</span>
                </div>
                <div class="status-row">
                    <div class="service-info"><h4>Swap Memory</h4><p>Virtual Memory Buffer</p></div>
                    <span style="color: #cbd5e1; font-size: 0.9rem; font-weight: 600;">2.0 GB Active</span>
                </div>
            </div>
        </div>

        <!-- TAB 4: Incident Logs -->
        <div id="incidents" class="tab-content">
            <div class="panel">
                <div class="panel-title">System Deployment Timeline</div>
                <div class="timeline-item">
                    <div class="timeline-date">Today - Active Version</div>
                    <div class="timeline-text">Deployed Glowing Branding Header & Real-time Live Performance tab.</div>
                </div>
                <div class="timeline-item">
                    <div class="timeline-date">Previous Session</div>
                    <div class="timeline-text">Configured Nginx Reverse Proxy on Port 80 with SELinux network rules.</div>
                </div>
                <div class="timeline-item" style="padding-bottom: 0;">
                    <div class="timeline-date">Project Initialization</div>
                    <div class="timeline-text">Deployed PostgreSQL container and initialized source control via GitHub.</div>
                </div>
            </div>
        </div>

        <!-- Footer -->
        <div class="footer">
            Engineered with ❤️ by <strong>Zeeshan Riaz</strong>
        </div>
    </div>

    <script>
        function switchTab(evt, tabId) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
            
            document.getElementById(tabId).classList.add('active');
            evt.currentTarget.classList.add('active');
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
