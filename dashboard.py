import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
import threading
import webbrowser

# ==========================================
# CONFIGURATION
# ==========================================

REPORT_FILE = "litelm_forge_report.json"
ANALYSIS_FILE = "litelm_forge_analysis.json"
PORT = 8000

# ==========================================
# DASHBOARD HTML
# ==========================================

DASHBOARD_HTML = """<!DOCTYPE html>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LiteLM Forge - Professional Dashboard</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
            background: #0f0f1e;
            color: #e0e0e0;
            min-height: 100vh;
            padding-bottom: 50px;
        }

        /* Navigation */
        .navbar {
            background: #1a1a2e;
            border-bottom: 1px solid #2a2a4e;
            padding: 0 40px;
            position: sticky;
            top: 0;
            z-index: 100;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }

        .navbar-content {
            max-width: 1600px;
            margin: 0 auto;
            display: flex;
            align-items: center;
            justify-content: space-between;
            height: 70px;
        }

        .logo {
            font-size: 1.4em;
            font-weight: 700;
            color: #00d4ff;
            letter-spacing: 1px;
        }

        .nav-links {
            display: flex;
            gap: 30px;
            list-style: none;
        }

        .nav-links a {
            color: #b0b0d0;
            text-decoration: none;
            font-weight: 500;
            padding: 8px 16px;
            border-radius: 8px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            cursor: pointer;
        }

        .nav-links a:hover {
            color: #00d4ff;
            background: rgba(0, 212, 255, 0.1);
        }

        .nav-links a.active {
            color: #00d4ff;
            background: rgba(0, 212, 255, 0.15);
            border-bottom: 2px solid #00d4ff;
        }

        /* Page container */
        .container {
            max-width: 1600px;
            margin: 40px auto;
            padding: 0 40px;
        }

        /* Page transitions */
        .page {
            display: none;
            animation: fadeIn 0.4s ease-in-out;
            opacity: 0;
        }

        .page.active {
            display: block;
            animation: fadeIn 0.5s ease-in-out;
            opacity: 1;
        }

        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        /* Grid layouts */
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 24px;
            margin-bottom: 40px;
        }

        .grid-2 {
            grid-template-columns: repeat(2, 1fr);
        }

        @media (max-width: 1200px) {
            .grid-2 {
                grid-template-columns: 1fr;
            }
        }

        /* Cards */
        .card {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            border: 1px solid #2a2a4e;
            padding: 28px;
            border-radius: 12px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .card:hover {
            border-color: #00d4ff;
            box-shadow: 0 8px 32px rgba(0, 212, 255, 0.15);
            transform: translateY(-2px);
        }

        .card h3 {
            color: #b0b0d0;
            font-size: 0.85em;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            margin-bottom: 16px;
            font-weight: 600;
        }

        .card .value {
            font-size: 2.8em;
            font-weight: 700;
            color: #00d4ff;
            margin-bottom: 12px;
        }

        .card .label {
            color: #7a7a9e;
            font-size: 0.95em;
        }

        /* Progress bar */
        .progress-bar {
            width: 100%;
            height: 6px;
            background: #2a2a4e;
            border-radius: 10px;
            overflow: hidden;
            margin-top: 16px;
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #00d4ff, #0099cc);
            transition: width 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            border-radius: 10px;
        }

        /* Section headers */
        h2 {
            color: #e0e0e0;
            font-size: 1.8em;
            margin-bottom: 32px;
            font-weight: 600;
            letter-spacing: 0.5px;
        }

        h3 {
            color: #e0e0e0;
            margin-bottom: 20px;
            font-weight: 600;
        }

        /* Charts container */
        .chart-container {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            border: 1px solid #2a2a4e;
            padding: 28px;
            border-radius: 12px;
            margin-bottom: 32px;
            position: relative;
            height: 400px;
        }

        .chart-wrapper {
            position: relative;
            height: 100%;
        }

        /* Tables */
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 32px;
        }

        th {
            background: rgba(0, 212, 255, 0.1);
            border-bottom: 2px solid #00d4ff;
            padding: 16px;
            text-align: left;
            color: #00d4ff;
            font-weight: 600;
            font-size: 0.95em;
            text-transform: uppercase;
            letter-spacing: 0.8px;
        }

        td {
            padding: 16px;
            border-bottom: 1px solid #2a2a4e;
            color: #b0b0d0;
        }

        tr:hover {
            background: rgba(0, 212, 255, 0.05);
        }

        /* Badges */
        .badge {
            display: inline-block;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
        }

        .badge-pass {
            background: rgba(0, 200, 100, 0.2);
            color: #00c864;
        }

        .badge-fail {
            background: rgba(255, 100, 100, 0.2);
            color: #ff6464;
        }

        .badge-warning {
            background: rgba(255, 165, 0, 0.2);
            color: #ffa500;
        }

        /* Scores */
        .score {
            font-weight: 700;
            font-size: 1.1em;
        }

        .score-high {
            color: #00c864;
        }

        .score-medium {
            color: #ffa500;
        }

        .score-low {
            color: #ff6464;
        }

        /* Report view */
        .report-item {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            border: 1px solid #2a2a4e;
            padding: 32px;
            border-radius: 12px;
            margin-bottom: 24px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .report-item:hover {
            border-color: #00d4ff;
            box-shadow: 0 8px 32px rgba(0, 212, 255, 0.1);
        }

        .report-item h4 {
            color: #00d4ff;
            margin-bottom: 16px;
            font-size: 1.2em;
        }

        .report-item .meta {
            display: flex;
            gap: 20px;
            margin-bottom: 16px;
            flex-wrap: wrap;
        }

        .meta-item {
            display: flex;
            flex-direction: column;
        }

        .meta-label {
            color: #7a7a9e;
            font-size: 0.85em;
            margin-bottom: 4px;
        }

        .meta-value {
            color: #e0e0e0;
            font-weight: 600;
        }

        /* Pie chart container */
        .pie-container {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            border: 1px solid #2a2a4e;
            padding: 28px;
            border-radius: 12px;
            margin-bottom: 32px;
            position: relative;
            min-height: 300px;
        }

        .pie-label {
            color: #00d4ff;
            font-size: 1.1em;
            font-weight: 600;
            margin-bottom: 16px;
        }

        .no-data {
            text-align: center;
            padding: 60px 20px;
            color: #7a7a9e;
        }

        /* Loading spinner */
        .loading {
            text-align: center;
            padding: 40px;
            color: #00d4ff;
        }

        .spinner {
            border: 3px solid #2a2a4e;
            border-top: 3px solid #00d4ff;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 0.8s linear infinite;
            margin: 0 auto 16px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        /* Code blocks */
        code {
            background: rgba(0, 212, 255, 0.05);
            padding: 2px 6px;
            border-radius: 4px;
            color: #00d4ff;
            font-family: 'Monaco', 'Courier New', monospace;
            font-size: 0.9em;
        }

        /* Grid layouts for pie charts */
        .pie-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 32px;
            margin-bottom: 32px;
        }

        /* Verdict text */
        .verdict {
            color: #b0b0d0;
            font-style: italic;
            margin-top: 12px;
            padding-top: 12px;
            border-top: 1px solid #2a2a4e;
        }

        /* Update time */
        .update-time {
            text-align: center;
            color: #7a7a9e;
            font-size: 0.9em;
            margin-top: 32px;
            padding-top: 20px;
            border-top: 1px solid #2a2a4e;
        }
    </style>
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar">
        <div class="navbar-content">
            <div class="logo">⚡ LiteLM Forge</div>
            <ul class="nav-links">
                <li><a class="nav-item active" onclick="switchPage('dashboard')">Dashboard</a></li>
                <li><a class="nav-item" onclick="switchPage('report')">Full Report</a></li>
                <li><a class="nav-item" onclick="switchPage('analysis')">Analysis</a></li>
            </ul>
        </div>
    </nav>

    <!-- Pages -->
    <div class="container">
        <!-- Dashboard Page -->
        <div id="dashboard" class="page active">
            <h2>Dashboard Overview</h2>
            
            <!-- Summary Cards -->
            <div class="grid">
                <div class="card">
                    <h3>📊 Total Tests</h3>
                    <div class="value" id="totalTests">0</div>
                    <div class="label">Across all sessions</div>
                </div>
                <div class="card">
                    <h3>✅ Pass Rate</h3>
                    <div class="value" id="passRate">0%</div>
                    <div class="progress-bar">
                        <div class="progress-fill" id="passRateBar" style="width: 0%"></div>
                    </div>
                </div>
                <div class="card">
                    <h3>📈 Avg Quality Score</h3>
                    <div class="value" id="avgScore">0<span style="font-size: 0.6em">/10</span></div>
                    <div class="label">Code quality</div>
                </div>
                <div class="card">
                    <h3>🤖 Sessions</h3>
                    <div class="value" id="sessionCount">0</div>
                    <div class="label">Testing runs</div>
                </div>
            </div>

            <!-- Model Comparison Chart -->
            <div class="chart-container">
                <h3>Model Performance Comparison</h3>
                <div class="chart-wrapper">
                    <canvas id="modelComparisonChart"></canvas>
                </div>
            </div>

            <!-- Pie Charts by Model -->
            <h3 style="margin-top: 40px;">Analysis Distribution by Model</h3>
            <div class="pie-grid" id="pieChartsContainer"></div>

            <div class="update-time" id="updateTime"></div>
        </div>

        <!-- Full Report Page -->
        <div id="report" class="page">
            <h2>Complete Test Report</h2>
            <div id="reportContainer" class="no-data">Loading report...</div>
            <div class="update-time" id="updateTimeReport"></div>
        </div>

        <!-- Analysis Page -->
        <div id="analysis" class="page">
            <h2>Code Quality Analysis</h2>
            <div id="analysisContainer" class="no-data">Loading analysis...</div>
            <div class="update-time" id="updateTimeAnalysis"></div>
        </div>
    </div>

    <script>
        let reportData = null;
        let analysisData = null;
        let modelComparisonChart = null;
        let pieCharts = {};

        async function loadData() {
            try {
                const reportRes = await fetch('/api/report');
                const analysisRes = await fetch('/api/analysis');
                
                reportData = await reportRes.json();
                analysisData = await analysisRes.json();

                updateDashboard();
                updateReportPage();
                updateAnalysisPage();

                const now = new Date();
                document.getElementById('updateTime').textContent = `Last updated: ${now.toLocaleTimeString()}`;
                document.getElementById('updateTimeReport').textContent = `Last updated: ${now.toLocaleTimeString()}`;
                document.getElementById('updateTimeAnalysis').textContent = `Last updated: ${now.toLocaleTimeString()}`;
            } catch (error) {
                console.error('Error loading data:', error);
            }
        }

        function updateDashboard() {
            if (!reportData || !reportData.sessions) return;

            let totalTests = 0;
            let passedTests = 0;
            const allResults = [];
            const modelStats = {};

            reportData.sessions.forEach(session => {
                const modelName = session.model_name;
                if (!modelStats[modelName]) {
                    modelStats[modelName] = { total: 0, passed: 0, scores: {} };
                }

                session.results.forEach(result => {
                    allResults.push(result);
                    totalTests++;
                    if (result.passed) passedTests++;
                    
                    modelStats[modelName].total++;
                    if (result.passed) modelStats[modelName].passed++;
                    
                    const prompt = result.prompt_name || 'unknown';
                    if (!modelStats[modelName].scores[prompt]) {
                        modelStats[modelName].scores[prompt] = [];
                    }
                    modelStats[modelName].scores[prompt].push(result);
                });
            });

            const passRate = totalTests > 0 ? Math.round((passedTests / totalTests) * 100) : 0;

            let avgScore = 0;
            if (analysisData.analyses && analysisData.analyses.length > 0) {
                const scores = analysisData.analyses
                    .map(a => a.overall_score || 0)
                    .filter(s => s > 0);
                avgScore = scores.length > 0 
                    ? (scores.reduce((a, b) => a + b, 0) / scores.length).toFixed(1)
                    : 0;
            }

            document.getElementById('totalTests').textContent = totalTests;
            document.getElementById('passRate').textContent = passRate + '%';
            document.getElementById('passRateBar').style.width = passRate + '%';
            document.getElementById('avgScore').textContent = avgScore;
            document.getElementById('sessionCount').textContent = reportData.sessions.length;

            updateModelComparisonChart(modelStats);
            updatePieCharts(modelStats);
        }

        function updateModelComparisonChart(modelStats) {
            const models = Object.keys(modelStats);
            const allPrompts = new Set();
            
            Object.values(modelStats).forEach(stats => {
                Object.keys(stats.scores).forEach(p => allPrompts.add(p));
            });
            
            const prompts = Array.from(allPrompts);
            const datasets = models.map((model, idx) => {
                const colors = ['#00d4ff', '#00c864', '#ffa500'];
                return {
                    label: model,
                    data: prompts.map(p => 
                        modelStats[model].scores[p] 
                            ? modelStats[model].scores[p].length 
                            : 0
                    ),
                    backgroundColor: colors[idx % colors.length],
                    borderColor: colors[idx % colors.length],
                    borderWidth: 2,
                    borderRadius: 8,
                };
            });

            const ctx = document.getElementById('modelComparisonChart');
            if (modelComparisonChart) modelComparisonChart.destroy();

            modelComparisonChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: prompts,
                    datasets: datasets
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            labels: { color: '#b0b0d0', font: { size: 12 } }
                        }
                    },
                    scales: {
                        y: {
                            ticks: { color: '#7a7a9e' },
                            grid: { color: '#2a2a4e' },
                            beginAtZero: true
                        },
                        x: {
                            ticks: { color: '#7a7a9e' },
                            grid: { color: '#2a2a4e' }
                        }
                    }
                }
            });
        }

        function updatePieCharts(modelStats) {
            const container = document.getElementById('pieChartsContainer');
            container.innerHTML = '';

            Object.keys(modelStats).forEach((model, idx) => {
                const stats = modelStats[model];
                const passed = stats.passed;
                const failed = stats.total - stats.passed;

                const div = document.createElement('div');
                div.className = 'pie-container';
                div.innerHTML = `
                    <div class="pie-label">${model}</div>
                    <canvas id="pieChart${idx}" style="max-height: 250px;"></canvas>
                `;
                container.appendChild(div);

                setTimeout(() => {
                    const ctx = document.getElementById(`pieChart${idx}`);
                    if (!ctx) return;

                    new Chart(ctx, {
                        type: 'doughnut',
                        data: {
                            labels: ['Passed', 'Failed'],
                            datasets: [{
                                data: [passed, failed],
                                backgroundColor: ['#00c864', '#ff6464'],
                                borderColor: ['#00c864', '#ff6464'],
                                borderWidth: 2
                            }]
                        },
                        options: {
                            responsive: true,
                            plugins: {
                                legend: {
                                    labels: { color: '#b0b0d0' }
                                }
                            }
                        }
                    });
                }, 100);
            });
        }

        function updateReportPage() {
            if (!reportData || !reportData.sessions) {
                document.getElementById('reportContainer').innerHTML = '<div class="no-data">No test data available</div>';
                return;
            }

            let html = '';
            let testIndex = 0;

            reportData.sessions.forEach(session => {
                session.results.forEach(result => {
                    testIndex++;
                    const status = result.passed 
                        ? '<span class="badge badge-pass">✅ PASSED</span>'
                        : '<span class="badge badge-fail">❌ FAILED</span>';
                    
                    const time = result.timestamp 
                        ? new Date(result.timestamp).toLocaleString()
                        : 'N/A';

                    html += `
                        <div class="report-item">
                            <h4>Test #${testIndex}: ${result.prompt_name}</h4>
                            <div class="meta">
                                <div class="meta-item">
                                    <span class="meta-label">Status</span>
                                    <span class="meta-value">${status}</span>
                                </div>
                                <div class="meta-item">
                                    <span class="meta-label">Model</span>
                                    <span class="meta-value">${result.model_name}</span>
                                </div>
                                <div class="meta-item">
                                    <span class="meta-label">Return Code</span>
                                    <span class="meta-value"><code>${result.return_code}</code></span>
                                </div>
                                <div class="meta-item">
                                    <span class="meta-label">Time</span>
                                    <span class="meta-value">${time}</span>
                                </div>
                            </div>
                            <div style="border-top: 1px solid #2a2a4e; padding-top: 16px; margin-top: 16px;">
                                <div style="margin-bottom: 12px;">
                                    <span style="color: #7a7a9e; font-size: 0.9em;">Prompt:</span>
                                    <div style="color: #b0b0d0; margin-top: 8px;">${result.prompt_text}</div>
                                </div>
                            </div>
                        </div>
                    `;
                });
            });

            document.getElementById('reportContainer').innerHTML = html;
        }

        function updateAnalysisPage() {
            if (!analysisData || !analysisData.analyses || analysisData.analyses.length === 0) {
                document.getElementById('analysisContainer').innerHTML = '<div class="no-data">No analysis data available</div>';
                return;
            }

            let html = '';

            analysisData.analyses.forEach((analysis, idx) => {
                const score = analysis.overall_score || 0;
                const scoreClass = score >= 7 ? 'score-high' : score >= 4 ? 'score-medium' : 'score-low';
                const status = analysis.passed 
                    ? '<span class="badge badge-pass">✅ PASSED</span>'
                    : '<span class="badge badge-warning">⚠️ FAILED</span>';

                const time = analysis.timestamp 
                    ? new Date(analysis.timestamp).toLocaleString()
                    : 'N/A';

                html += `
                    <div class="report-item">
                        <h4>Analysis #${idx + 1}: ${analysis.prompt_name}</h4>
                        <div class="meta">
                            <div class="meta-item">
                                <span class="meta-label">Quality Score</span>
                                <span class="meta-value"><span class="score ${scoreClass}">${score}/10</span></span>
                            </div>
                            <div class="meta-item">
                                <span class="meta-label">Status</span>
                                <span class="meta-value">${status}</span>
                            </div>
                            <div class="meta-item">
                                <span class="meta-label">Model</span>
                                <span class="meta-value">${analysis.model_name}</span>
                            </div>
                            <div class="meta-item">
                                <span class="meta-label">Judge Model</span>
                                <span class="meta-value">${analysisData.judge_model || 'Unknown'}</span>
                            </div>
                            <div class="meta-item">
                                <span class="meta-label">Analyzed</span>
                                <span class="meta-value">${time}</span>
                            </div>
                        </div>

                        <div style="margin-top: 16px; padding-top: 16px; border-top: 1px solid #2a2a4e;">
                            <div style="margin-bottom: 16px;">
                                <div style="color: #7a7a9e; font-size: 0.9em; margin-bottom: 8px;">Strengths:</div>
                                <div style="color: #00c864;">
                                    ${(analysis.strengths || []).map(s => `• ${s}`).join('<br>')}
                                </div>
                            </div>
                            
                            <div style="margin-bottom: 16px;">
                                <div style="color: #7a7a9e; font-size: 0.9em; margin-bottom: 8px;">Issues:</div>
                                <div style="color: #ff6464;">
                                    ${(analysis.issues || []).map(i => `• ${i}`).join('<br>')}
                                </div>
                            </div>

                            <div class="verdict">
                                <strong>Verdict:</strong> ${analysis.verdict || 'No verdict available'}
                            </div>
                        </div>
                    </div>
                `;
            });

            document.getElementById('analysisContainer').innerHTML = html;
        }

        function switchPage(pageName) {
            // Update active nav item
            document.querySelectorAll('.nav-item').forEach(item => {
                item.classList.remove('active');
            });
            event.target.classList.add('active');

            // Update active page
            document.querySelectorAll('.page').forEach(page => {
                page.classList.remove('active');
            });
            document.getElementById(pageName).classList.add('active');
        }

        // Load data on startup and every 5 seconds
        loadData();
        setInterval(loadData, 5000);
    </script>
</body>
</html>"""

# ==========================================
# WEB SERVER
# ==========================================

class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(DASHBOARD_HTML.encode())
        
        elif self.path == "/api/report":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            
            try:
                with open(REPORT_FILE, "r") as f:
                    data = json.load(f)
                self.wfile.write(json.dumps(data).encode())
            except FileNotFoundError:
                self.wfile.write(json.dumps({"sessions": []}).encode())
        
        elif self.path == "/api/analysis":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            
            try:
                with open(ANALYSIS_FILE, "r") as f:
                    data = json.load(f)
                self.wfile.write(json.dumps(data).encode())
            except FileNotFoundError:
                self.wfile.write(json.dumps({"analyses": [], "summary": {}}).encode())
        
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass

# ==========================================
# MAIN
# ==========================================

def start_server():
    """Start web server"""
    server = HTTPServer(("localhost", PORT), DashboardHandler)
    print(f"\n✅ Dashboard running at: http://localhost:{PORT}")
    print(f"📊 Auto-refresh every 5 seconds")
    print(f"🔒 Press Ctrl+C to stop\n")
    
    server.serve_forever()

if __name__ == "__main__":
    print("🚀 Starting LiteLM Forge Dashboard Server...")
    
    # Start server in background
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Open browser
    import time
    time.sleep(1)
    webbrowser.open(f"http://localhost:{PORT}")
    
    # Keep running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped")