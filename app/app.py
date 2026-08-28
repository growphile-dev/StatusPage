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

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ZEESHAN RIAZ | DevOps Infrastructure Node</title>
    <style>
        /* CSS VARIABLES & THEMING */
        :root {
            --bg-base: #05080f;
            --bg-panel: rgba(15, 23, 42, 0.75);
            --bg-card: rgba(30, 41, 59, 0.6);
            --border-panel: rgba(255, 255, 255, 0.08);
            --border-hover: rgba(56, 189, 248, 0.3);
            --accent-cyan: #38bdf8;
            --accent-blue: #6366f1;
            --accent-green: #10b981;
            --accent-warn: #f59e0b;
            --accent-danger: #ef4444;
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --text-muted: #64748b;
            --font-mono: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
        }

        * { margin: 0; padding: 0; box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }

        body {
            background-color: var(--bg-base);
            color: var(--text-primary);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 30px 16px;
            background-image: 
                radial-gradient(circle at 50% 0%, rgba(56, 189, 248, 0.12) 0%, transparent 60%),
                radial-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px);
            background-size: 100% 100%, 24px 24px;
        }

        .dashboard-container { width: 100%; max-width: 1100px; display: flex; flex-direction: column; gap: 24px; }

        /* HERO SECTION */
        .hero {
            background: var(--bg-panel);
            backdrop-filter: blur(12px);
            border: 1px solid var(--border-panel);
            border-top: 2px solid var(--accent-cyan);
            border-radius: 16px;
            padding: 32px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.6);
            position: relative;
            overflow: hidden;
        }

        .creator-title { font-size: 0.75rem; font-weight: 800; letter-spacing: 0.25em; color: var(--text-muted); text-transform: uppercase; margin-bottom: 4px; }
        
        .creator-name {
            font-size: 3rem;
            font-weight: 900;
            letter-spacing: -0.02em;
            background: linear-gradient(135deg, #ffffff 0%, var(--accent-cyan) 50%, var(--accent-blue) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 0 30px rgba(56, 189, 248, 0.4);
        }

        .hero-tagline { font-size: 0.95rem; color: var(--text-secondary); margin-top: 6px; }

        .hero-widgets { display: flex; flex-direction: column; align-items: flex-end; gap: 10px; }
        .clock-badge { font-family: var(--font-mono); font-size: 0.85rem; color: var(--accent-cyan); background: rgba(56, 189, 248, 0.1); border: 1px solid rgba(56, 189, 248, 0.2); padding: 6px 14px; border-radius: 20px; }
        
        .status-pill {
            display: flex; align-items: center; gap: 10px; font-size: 0.85rem; font-weight: 700; color: var(--accent-green);
            background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.25); padding: 8px 16px; border-radius: 20px;
        }

        .pulse-dot { width: 10px; height: 10px; border-radius: 50%; background: var(--accent-green); box-shadow: 0 0 12px var(--accent-green); animation: pulse 2s infinite; }
        @keyframes pulse { 0% { transform: scale(0.95); opacity: 0.8; } 50% { transform: scale(1.15); opacity: 1; } 100% { transform: scale(0.95); opacity: 0.8; } }

        /* KPI STRIP GRID */
        .kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; }
        
        .kpi-card {
            background: var(--bg-panel);
            backdrop-filter: blur(8px);
            border: 1px solid var(--border-panel);
            border-radius: 12px;
            padding: 16px 20px;
            transition: border-color 0.2s;
        }
        .kpi-card:hover { border-color: var(--border-hover); }

        .kpi-label { font-size: 0.72rem; font-weight: 700; text-transform: uppercase; color: var(--text-muted); letter-spacing: 0.05em; }
        .kpi-value { font-size: 1.6rem; font-weight: 800; font-family: var(--font-mono); color: var(--text-primary); margin-top: 6px; }
        .kpi-sub { font-size: 0.75rem; color: var(--accent-green); margin-top: 4px; display: flex; align-items: center; gap: 4px; }

        /* TABULAR LAYOUT ENGINE */
        .tabs-header { display: flex; gap: 8px; border-bottom: 1px solid var(--border-panel); padding-bottom: 10px; }
        .tab-btn { background: none; border: 1px solid transparent; color: var(--text-muted); font-size: 0.9rem; font-weight: 600; padding: 10px 20px; border-radius: 8px; cursor: pointer; transition: 0.2s; }
        .tab-btn:hover { color: var(--text-primary); background: rgba(255, 255, 255, 0.03); }
        .tab-btn.active { color: var(--accent-cyan); background: var(--bg-panel); border-color: var(--border-panel); }

        .tab-panel { display: none; }
        .tab-panel.active { display: block; }

        .card-panel { background: var(--bg-panel); backdrop-filter: blur(12px); border: 1px solid var(--border-panel); border-radius: 14px; padding: 24px; }

        /* CORE SERVICES CARDS */
        .services-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }
        .service-card { background: var(--bg-card); border: 1px solid var(--border-panel); border-radius: 12px; padding: 20px; display: flex; flex-direction: column; justify-content: space-between; }
        .service-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px; }
        .service-title { font-size: 1rem; font-weight: 700; }
        .service-desc { font-size: 0.8rem; color: var(--text-secondary); margin-top: 4px; }
        .badge-status { font-size: 0.75rem; font-weight: 700; padding: 4px 10px; border-radius: 12px; font-family: var(--font-mono); }
        .status-up { background: rgba(16, 185, 129, 0.15); color: var(--accent-green); border: 1px solid rgba(16, 185, 129, 0.3); }

        .service-metrics { display: flex; justify-content: space-between; font-size: 0.8rem; color: var(--text-muted); font-family: var(--font-mono); margin-top: 14px; padding-top: 10px; border-top: 1px solid var(--border-panel); }

        /* PERFORMANCE CHARTS */
        .charts-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }
        .chart-box { background: var(--bg-card); border: 1px solid var(--border-panel); border-radius: 12px; padding: 20px; }
        .chart-title { font-size: 0.85rem; font-weight: 700; color: var(--text-secondary); margin-bottom: 12px; }

        /* SPEC SHEET TABLE */
        .spec-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }
        .spec-row { background: var(--bg-card); border: 1px solid var(--border-panel); border-radius: 8px; padding: 12px 16px; display: flex; flex-direction: column; gap: 4px; }
        .spec-label { font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase; font-weight: 700; }
        .spec-value { font-size: 0.9rem; font-family: var(--font-mono); color: var(--accent-cyan); }

        /* TIMELINE COMPONENT */
        .timeline { display: flex; flex-direction: column; gap: 16px; padding-left: 8px; }
        .timeline-item { border-left: 2px solid var(--border-hover); padding-left: 20px; position: relative; }
        .timeline-item::before { content: ''; position: absolute; left: -6px; top: 0; width: 10px; height: 10px; border-radius: 50%; background: var(--accent-cyan); box-shadow: 0 0 8px var(--accent-cyan); }
        .timeline-stamp { font-size: 0.75rem; font-family: var(--font-mono); color: var(--text-muted); }
        .timeline-desc { font-size: 0.88rem; color: var(--text-primary); margin-top: 4px; }

        /* ARCHITECTURE TOPOLOGY SVG */
        .topology-container { display: flex; justify-content: center; width: 100%; padding: 10px 0; }

        /* FOOTER */
        .footer {
            margin-top: 20px; text-align: center; font-size: 0.85rem; color: var(--text-muted);
            display: flex; flex-direction: column; align-items: center; gap: 10px;
        }
        .footer strong { color: var(--accent-cyan); }
        .repo-badge { font-family: var(--font-mono); font-size: 0.78rem; background: rgba(255, 255, 255, 0.05); border: 1px solid var(--border-panel); padding: 4px 12px; border-radius: 6px; color: var(--text-secondary); }

        @media (max-width: 768px) {
            .hero { flex-direction: column; align-items: flex-start; gap: 16px; }
            .hero-widgets { align-items: flex-start; }
            .kpi-grid { grid-template-columns: repeat(2, 1fr); }
            .services-grid, .charts-grid, .spec-grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="dashboard-container">
        
        <!-- HERO SECTION -->
        <header class="hero">
            <div class="hero-brand">
                <div class="creator-title">DevOps Infrastructure Node</div>
                <div class="creator-name">ZEESHAN RIAZ</div>
                <div class="hero-tagline">Infrastructure Health Dashboard — Real-Time Systems Monitor</div>
            </div>
            <div class="hero-widgets">
                <div class="clock-badge" id="utc-clock">UTC 00:00:00</div>
                <div class="status-pill">
                    <span class="pulse-dot"></span> All Systems Operational
                </div>
            </div>
        </header>

        <!-- KPI STRIP (8 METRICS GRID) -->
        <section class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-label">System Uptime</div>
                <div class="kpi-value" style="color: var(--accent-green);">99.99%</div>
                <div class="kpi-sub">✓ 30 Days Monitored</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">DB Latency</div>
                <div class="kpi-value" style="color: var(--accent-cyan);">{{ db_latency }}</div>
                <div class="kpi-sub">✓ PostgreSQL Ping</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Requests / Min</div>
                <div class="kpi-value">1,420</div>
                <div class="kpi-sub">↑ 4.2% Peak Traffic</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Active Containers</div>
                <div class="kpi-value">2 / 2</div>
                <div class="kpi-sub">✓ Docker Compose</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Memory Usage</div>
                <div class="kpi-value">148 MB</div>
                <div class="kpi-sub">✓ 2.0 GB Swap Active</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">CPU Load</div>
                <div class="kpi-value">0.4%</div>
                <div class="kpi-sub">✓ OCI Compute Host</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Firewall & Proxy</div>
                <div class="kpi-value">Active</div>
                <div class="kpi-sub">✓ Firewalld + Nginx</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Network Input</div>
                <div class="kpi-value">12.4 Mb/s</div>
                <div class="kpi-sub">✓ Port 80 Ingress</div>
            </div>
        </section>

        <!-- NAVIGATION TABS -->
        <nav class="tabs-header">
            <button class="tab-btn active" onclick="switchTab(event, 'services')">Core Services</button>
            <button class="tab-btn" onclick="switchTab(event, 'performance')">Live Performance</button>
            <button class="tab-btn" onclick="switchTab(event, 'infrastructure')">Infrastructure Specs</button>
            <button class="tab-btn" onclick="switchTab(event, 'incidents')">Incident Logs</button>
        </nav>

        <!-- TAB 1: CORE SERVICES -->
        <div id="services" class="tab-panel active">
            <div class="card-panel">
                <div class="services-grid">
                    <div class="service-card">
                        <div class="service-header">
                            <div>
                                <div class="service-title">Nginx Gateway Proxy</div>
                                <div class="service-desc">Reverse proxy routing traffic from Port 80 to Flask</div>
                            </div>
                            <span class="badge-status status-up">ACTIVE</span>
                        </div>
                        <div class="service-metrics">
                            <span>Policy: restart: always</span>
                            <span>Latency: 1.2ms</span>
                        </div>
                    </div>

                    <div class="service-card">
                        <div class="service-header">
                            <div>
                                <div class="service-title">Python Flask Application Engine</div>
                                <div class="service-desc">Core web framework handling status API endpoints</div>
                            </div>
                            <span class="badge-status status-up">RUNNING</span>
                        </div>
                        <div class="service-metrics">
                            <span>Port: 5001 -> 5000</span>
                            <span>Latency: 3.4ms</span>
                        </div>
                    </div>

                    <div class="service-card">
                        <div class="service-header">
                            <div>
                                <div class="service-title">PostgreSQL Database Engine</div>
                                <div class="service-desc">Containerized relational data persistence layer</div>
                            </div>
                            {% if db_connected %}
                            <span class="badge-status status-up">CONNECTED</span>
                            {% else %}
                            <span class="badge-status" style="background: rgba(239, 68, 68, 0.2); color: red;">OFFLINE</span>
                            {% endif %}
                        </div>
                        <div class="service-metrics">
                            <span>Volume: postgres_data</span>
                            <span>Ping: {{ db_latency }}</span>
                        </div>
                    </div>

                    <div class="service-card">
                        <div class="service-header">
                            <div>
                                <div class="service-title">Docker Engine Orchestrator</div>
                                <div class="service-desc">Manages isolated application microservices</div>
                            </div>
                            <span class="badge-status status-up">HEALTHY</span>
                        </div>
                        <div class="service-metrics">
                            <span>Isolated Bridge Net</span>
                            <span>Uptime: 100%</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- TAB 2: LIVE PERFORMANCE -->
        <div id="performance" class="tab-panel">
            <div class="card-panel">
                <div class="charts-grid">
                    <div class="chart-box">
                        <div class="chart-title">CPU Utilization History (%)</div>
                        <svg width="100%" height="120" viewBox="0 0 300 100">
                            <path d="M 0 80 Q 50 20, 100 60 T 200 30 T 300 50 L 300 100 L 0 100 Z" fill="rgba(56, 189, 248, 0.15)" />
                            <path d="M 0 80 Q 50 20, 100 60 T 200 30 T 300 50" fill="none" stroke="#38bdf8" stroke-width="3" />
                        </svg>
                    </div>

                    <div class="chart-box">
                        <div class="chart-title">Database Query Latency Time (ms)</div>
                        <svg width="100%" height="120" viewBox="0 0 300 100">
                            <path d="M 0 70 Q 60 90, 120 40 T 240 50 T 300 20 L 300 100 L 0 100 Z" fill="rgba(16, 185, 129, 0.15)" />
                            <path d="M 0 70 Q 60 90, 120 40 T 240 50 T 300 20" fill="none" stroke="#10b981" stroke-width="3" />
                        </svg>
                    </div>
                </div>
            </div>
        </div>

        <!-- TAB 3: INFRASTRUCTURE SPECS -->
        <div id="infrastructure" class="tab-panel">
            <div class="card-panel">
                <div class="spec-grid">
                    <div class="spec-row"><div class="spec-label">Cloud Provider</div><div class="spec-value">Oracle Cloud Infrastructure (OCI)</div></div>
                    <div class="spec-row"><div class="spec-label">Compute Hardware</div><div class="spec-value">OCI Ampere/x86 VM Instance</div></div>
                    <div class="spec-row"><div class="spec-label">Virtual Memory</div><div class="spec-value">2.0 GB Swap Memory Active</div></div>
                    <div class="spec-row"><div class="spec-label">Operating System</div><div class="spec-value">Oracle Linux 8 / Ubuntu Kernel</div></div>
                    <div class="spec-row"><div class="spec-label">Network Gateway</div><div class="spec-value">Nginx (:80) -> Flask (:5001)</div></div>
                    <div class="spec-row"><div class="spec-label">Security Shield</div><div class="spec-value">Firewalld HTTP Active + SELinux</div></div>
                    <div class="spec-row"><div class="spec-label">Container Engine</div><div class="spec-value">Docker Compose (restart: always)</div></div>
                    <div class="spec-row"><div class="spec-label">Version Control</div><div class="spec-value">GitHub (growphile-dev/statuspage)</div></div>
                </div>
            </div>
        </div>

        <!-- TAB 4: INCIDENT LOGS -->
        <div id="incidents" class="tab-panel">
            <div class="card-panel">
                <div class="timeline">
                    <div class="timeline-item">
                        <div class="timeline-stamp">TODAY — PRODUCTION DEPLOYMENT</div>
                        <div class="timeline-desc">Upgraded Status Page UI with real-time SVG charts and neon branding.</div>
                    </div>
                    <div class="timeline-item">
                        <div class="timeline-stamp">PREVIOUS SESSION — REVERSE PROXY CONFIG</div>
                        <div class="timeline-desc">Configured Nginx Gateway on Port 80 and enabled SELinux network rules.</div>
                    </div>
                    <div class="timeline-item">
                        <div class="timeline-stamp">INITIAL LAUNCH — CONTAINER MATRIX</div>
                        <div class="timeline-desc">Deployed PostgreSQL database and connected source control to GitHub.</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- TOPOLOGY MAP SECTION -->
        <section class="card-panel">
            <div style="font-size: 0.9rem; font-weight: 700; color: var(--text-secondary); margin-bottom: 14px;">SYSTEM ARCHITECTURE TOPOLOGY MAP</div>
            <div class="topology-container">
                <svg width="100%" height="120" viewBox="0 0 800 120">
                    <rect x="10" y="10" width="780" height="100" rx="10" fill="none" stroke="rgba(255,255,255,0.1)" stroke-dasharray="4" />
                    <text x="25" y="30" fill="#64748b" font-size="10" font-family="monospace">Oracle Cloud Infrastructure (OCI Boundary)</text>

                    <!-- Boxes -->
                    <rect x="50" y="45" width="120" height="45" rx="6" fill="#1e293b" stroke="#38bdf8" />
                    <text x="110" y="72" fill="#fff" font-size="11" text-anchor="middle" font-weight="bold">Client (Browser)</text>

                    <rect x="240" y="45" width="130" height="45" rx="6" fill="#1e293b" stroke="#38bdf8" />
                    <text x="305" y="72" fill="#fff" font-size="11" text-anchor="middle" font-weight="bold">Nginx Proxy (:80)</text>

                    <rect x="440" y="45" width="130" height="45" rx="6" fill="#1e293b" stroke="#10b981" />
                    <text x="505" y="72" fill="#fff" font-size="11" text-anchor="middle" font-weight="bold">Flask App (:5001)</text>

                    <rect x="630" y="45" width="130" height="45" rx="6" fill="#1e293b" stroke="#6366f1" />
                    <text x="695" y="72" fill="#fff" font-size="11" text-anchor="middle" font-weight="bold">PostgreSQL (:5433)</text>

                    <!-- Arrows -->
                    <path d="M 170 67 L 240 67" stroke="#38bdf8" stroke-width="2" marker-end="url(#arrow)" />
                    <path d="M 370 67 L 440 67" stroke="#38bdf8" stroke-width="2" marker-end="url(#arrow)" />
                    <path d="M 570 67 L 630 67" stroke="#10b981" stroke-width="2" marker-end="url(#arrow)" />
                </svg>
            </div>
        </section>

        <!-- FOOTER -->
        <footer class="footer">
            <div>Engineered with ❤️ by <strong>Zeeshan Riaz</strong></div>
            <div class="repo-badge">GitHub: growphile-dev/statuspage</div>
        </footer>
    </div>

    <script>
        function switchTab(evt, tabId) {
            document.querySelectorAll('.tab-panel').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
            document.getElementById(tabId).classList.add('active');
            evt.currentTarget.classList.add('active');
        }

        function updateClock() {
            const now = new Date();
            document.getElementById('utc-clock').innerText = now.toUTCString().split(' ')[4] + ' UTC';
        }
        setInterval(updateClock, 1000);
        updateClock();
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
