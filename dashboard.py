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
# DASHBOARD HTML (Dark Neon Theme)
# ==========================================

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>⚡ LiteLM Forge - Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0f0f1f 0%, #1a1a2e 100%);
            min-height: 100vh;
            padding: 20px;
            color: #e0e0e0;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
        }

        .header {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 0 40px rgba(0, 255, 65, 0.2), 0 10px 40px rgba(0,0,0,0.3);
            margin-bottom: 0;
            text-align: center;
            border: 2px solid #00ff41;
        }

        .header h1 {
            font-size: 2.5em;
            background: linear-gradient(135deg, #00ff41, #00d4ff, #ffb800);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 10px;
            font-weight: 900;
            text-shadow: 0 0 20px rgba(0, 255, 65, 0.5);
        }

        .header p {
            color: #b0b0d0;
            font-size: 1.1em;
        }

        .nav-tabs {
            display: flex;
            gap: 0;
            background: #16213e;
            border-bottom: 3px solid #00ff41;
            padding: 0 30px;
            margin: 0;
            box-shadow: 0 0 30px rgba(0, 255, 65, 0.2);
        }

        .nav-tab {
            padding: 16px 24px;
            background: none;
            border: none;
            color: #888;
            font-size: 1em;
            font-weight: bold;
            cursor: pointer;
            border-bottom: 3px solid transparent;
            margin-bottom: -3px;
            transition: all 0.3s;
        }

        .nav-tab:hover {
            color: #ffb800;
            background: rgba(255, 184, 0, 0.1);
            box-shadow: inset 0 -2px 10px rgba(255, 184, 0, 0.2);
        }

        .nav-tab.active {
            color: #00ff41;
            border-bottom-color: #00ff41;
            box-shadow: 0 0 20px rgba(0, 255, 65, 0.4), inset 0 -2px 10px rgba(0, 255, 65, 0.2);
        }

        .content {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            border-radius: 0 0 15px 15px;
            box-shadow: 0 0 40px rgba(0, 255, 65, 0.2), 0 10px 40px rgba(0,0,0,0.3);
            border: 2px solid #00ff41;
            border-top: none;
            padding: 30px;
            margin-bottom: 30px;
        }

        .page {
            display: none;
            animation: fadeIn 0.3s;
        }

        .page.active {
            display: block;
        }

        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        .controls {
            display: flex;
            gap: 10px;
            margin-top: 20px;
            justify-content: center;
            flex-wrap: wrap;
        }

        button {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1em;
            font-weight: bold;
            transition: all 0.3s;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .btn-primary {
            background: linear-gradient(135deg, #00ff41, #00d4ff);
            color: #0f0f1f;
            box-shadow: 0 0 20px rgba(0, 255, 65, 0.5);
            border: 2px solid #00ff41;
        }

        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 0 30px rgba(0, 255, 65, 0.8), 0 5px 15px rgba(0, 255, 65, 0.3);
            color: #000;
        }

        .btn-secondary {
            background: rgba(255, 184, 0, 0.1);
            color: #ffb800;
            border: 2px solid #ffb800;
            box-shadow: 0 0 15px rgba(255, 184, 0, 0.3);
        }

        .btn-secondary:hover {
            background: rgba(255, 184, 0, 0.2);
            transform: translateY(-2px);
            box-shadow: 0 0 25px rgba(255, 184, 0, 0.6);
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .card {
            background: linear-gradient(135deg, rgba(0, 255, 65, 0.05), rgba(0, 212, 255, 0.05));
            padding: 25px;
            border-radius: 12px;
            border: 2px solid #00ff41;
            box-shadow: 0 0 20px rgba(0, 255, 65, 0.2);
        }

        .card:hover {
            border-color: #ffb800;
            box-shadow: 0 0 30px rgba(255, 184, 0, 0.4);
            background: linear-gradient(135deg, rgba(255, 184, 0, 0.05), rgba(255, 184, 0, 0.05));
        }

        .card h3 {
            color: #00ff41;
            margin-bottom: 15px;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
            text-shadow: 0 0 10px rgba(0, 255, 65, 0.5);
        }

        .card .value {
            font-size: 2.5em;
            font-weight: 900;
            background: linear-gradient(135deg, #00ff41, #ffb800);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 10px;
        }

        .card .label {
            color: #888;
            font-size: 0.95em;
        }

        .progress-bar {
            width: 100%;
            height: 8px;
            background: rgba(0, 255, 65, 0.1);
            border-radius: 10px;
            overflow: hidden;
            margin-top: 15px;
            border: 1px solid #00ff41;
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #00ff41, #ffb800);
            transition: width 0.3s;
            box-shadow: 0 0 10px rgba(0, 255, 65, 0.6);
        }

        .info-section {
            background: linear-gradient(135deg, rgba(0, 255, 65, 0.05), rgba(0, 212, 255, 0.05));
            border-radius: 12px;
            border: 2px solid #00d4ff;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 0 20px rgba(0, 212, 255, 0.2);
        }

        .info-title {
            font-size: 16px;
            font-weight: bold;
            color: #00d4ff;
            margin-bottom: 12px;
            text-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
        }

        .info-content {
            font-size: 14px;
            color: #b0b0d0;
            line-height: 1.6;
        }

        .models-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
        }

        .model-card {
            background: linear-gradient(135deg, rgba(0, 255, 65, 0.05), rgba(255, 184, 0, 0.05));
            border: 2px solid #ffb800;
            border-radius: 12px;
            padding: 20px;
            cursor: pointer;
            transition: all 0.3s;
            box-shadow: 0 0 15px rgba(255, 184, 0, 0.2);
        }

        .model-card:hover {
            border-color: #00ff41;
            background: linear-gradient(135deg, rgba(0, 255, 65, 0.1), rgba(0, 212, 255, 0.1));
            box-shadow: 0 0 30px rgba(0, 255, 65, 0.4), 0 0 15px rgba(255, 184, 0, 0.2);
            transform: translateY(-5px);
        }

        .model-card.selected {
            border: 2px solid #00ff41;
            background: linear-gradient(135deg, rgba(0, 255, 65, 0.15), rgba(0, 212, 255, 0.15));
            box-shadow: 0 0 40px rgba(0, 255, 65, 0.5);
        }

        .model-name {
            font-size: 16px;
            font-weight: bold;
            margin-bottom: 12px;
            color: #00ff41;
            text-shadow: 0 0 10px rgba(0, 255, 65, 0.5);
        }

        .model-meta {
            display: flex;
            flex-direction: column;
            gap: 8px;
            font-size: 13px;
            color: #888;
            margin-bottom: 12px;
            padding-bottom: 12px;
            border-bottom: 1px solid rgba(0, 255, 65, 0.3);
        }

        .model-meta div {
            display: flex;
            justify-content: space-between;
        }

        .model-stats {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            margin-bottom: 12px;
        }

        .stat-box {
            background: rgba(0, 255, 65, 0.1);
            padding: 12px;
            border-radius: 8px;
            text-align: center;
            border: 1px solid #00ff41;
        }

        .stat-num {
            font-size: 18px;
            font-weight: bold;
            color: #00ff41;
            text-shadow: 0 0 10px rgba(0, 255, 65, 0.5);
        }

        .stat-label {
            font-size: 11px;
            color: #666;
            margin-top: 4px;
        }

        .keywords {
            margin-top: 12px;
        }

        .keyword-label {
            font-size: 11px;
            font-weight: bold;
            color: #ffb800;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 6px;
        }

        .keyword-list {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
        }

        .keyword-tag {
            background: rgba(0, 212, 255, 0.1);
            border-radius: 6px;
            padding: 4px 10px;
            font-size: 12px;
            color: #00d4ff;
            border: 1px solid #00d4ff;
        }

        .keyword-tag.good {
            background: rgba(0, 255, 65, 0.15);
            color: #00ff41;
            border-color: #00ff41;
        }

        .keyword-tag.bad {
            background: rgba(255, 50, 100, 0.15);
            color: #ff3264;
            border-color: #ff3264;
        }

        .table-container {
            margin-bottom: 30px;
        }

        .table-container h3 {
            color: #00ff41;
            margin-bottom: 20px;
            font-size: 1.2em;
            font-weight: bold;
            text-shadow: 0 0 10px rgba(0, 255, 65, 0.5);
        }

        table {
            width: 100%;
            border-collapse: collapse;
        }

        th {
            background: rgba(0, 255, 65, 0.1);
            padding: 15px;
            text-align: left;
            font-weight: bold;
            color: #00ff41;
            border-bottom: 2px solid #00ff41;
            box-shadow: 0 0 10px rgba(0, 255, 65, 0.3);
        }

        td {
            padding: 12px 15px;
            border-bottom: 1px solid rgba(0, 255, 65, 0.2);
            color: #b0b0d0;
        }

        tr:hover {
            background: rgba(0, 255, 65, 0.05);
        }

        .badge {
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: bold;
        }

        .badge-pass {
            background: rgba(0, 255, 65, 0.2);
            color: #00ff41;
            border: 1px solid #00ff41;
        }

        .badge-fail {
            background: rgba(255, 50, 100, 0.2);
            color: #ff3264;
            border: 1px solid #ff3264;
        }

        .badge-warning {
            background: rgba(255, 184, 0, 0.2);
            color: #ffb800;
            border: 1px solid #ffb800;
        }

        .score {
            font-weight: bold;
            font-size: 1.1em;
        }

        .score.high {
            color: #00ff41;
            text-shadow: 0 0 10px rgba(0, 255, 65, 0.5);
        }

        .score.medium {
            color: #ffb800;
            text-shadow: 0 0 10px rgba(255, 184, 0, 0.5);
        }

        .score.low {
            color: #ff3264;
            text-shadow: 0 0 10px rgba(255, 50, 100, 0.5);
        }

        .chart-container {
            margin-bottom: 30px;
        }

        .chart-container h3 {
            color: #00ff41;
            margin-bottom: 20px;
            font-weight: bold;
            text-shadow: 0 0 10px rgba(0, 255, 65, 0.5);
        }

        .bar-chart {
            display: flex;
            gap: 30px;
            flex-wrap: wrap;
        }

        .bar-item {
            flex: 1;
            min-width: 150px;
        }

        .bar-label {
            font-size: 0.9em;
            color: #ffb800;
            margin-bottom: 8px;
            font-weight: bold;
        }

        .bar-background {
            height: 30px;
            background: rgba(0, 255, 65, 0.1);
            border-radius: 5px;
            overflow: hidden;
            border: 1px solid #00ff41;
        }

        .bar-fill {
            height: 100%;
            background: linear-gradient(90deg, #00ff41, #ffb800);
            display: flex;
            align-items: center;
            justify-content: flex-end;
            padding-right: 10px;
            color: #000;
            font-weight: bold;
            font-size: 0.9em;
            box-shadow: 0 0 15px rgba(0, 255, 65, 0.5);
        }

        .no-data {
            text-align: center;
            padding: 40px;
            color: #666;
        }

        .session-item {
            padding: 15px;
            background: rgba(0, 255, 65, 0.05);
            border-radius: 10px;
            margin-bottom: 10px;
            cursor: pointer;
            transition: all 0.3s;
            border: 1px solid rgba(0, 255, 65, 0.3);
        }

        .session-item:hover {
            background: rgba(0, 255, 65, 0.1);
            border-color: #ffb800;
            transform: translateX(5px);
            box-shadow: 0 0 20px rgba(255, 184, 0, 0.3);
        }

        .session-time {
            color: #888;
            font-size: 0.9em;
        }

        .refresh-time {
            text-align: center;
            color: #666;
            font-size: 0.9em;
            margin-top: 20px;
        }

        .analysis-section {
            margin-bottom: 20px;
        }

        .analysis-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-top: 20px;
        }

        .analysis-card {
            background: linear-gradient(135deg, rgba(0, 255, 65, 0.05), rgba(0, 212, 255, 0.05));
            border-radius: 12px;
            border: 2px solid #00ff41;
            padding: 20px;
            text-align: center;
            box-shadow: 0 0 15px rgba(0, 255, 65, 0.2);
        }

        .analysis-metric {
            font-size: 12px;
            color: #888;
            margin-bottom: 10px;
            text-transform: uppercase;
            font-weight: bold;
        }

        .analysis-value {
            font-size: 32px;
            font-weight: bold;
            color: #00ff41;
            text-shadow: 0 0 20px rgba(0, 255, 65, 0.5);
        }

        .select-label {
            display: block;
            font-size: 14px;
            font-weight: bold;
            margin-bottom: 12px;
            color: #00ff41;
        }

        select {
            width: 100%;
            padding: 12px;
            border-radius: 8px;
            border: 2px solid #00ff41;
            font-size: 14px;
            margin-bottom: 20px;
            background: rgba(0, 255, 65, 0.1);
            color: #00ff41;
            font-weight: bold;
            box-shadow: 0 0 15px rgba(0, 255, 65, 0.3);
        }

        select:hover {
            border-color: #ffb800;
            box-shadow: 0 0 20px rgba(255, 184, 0, 0.4);
        }

        select:focus {
            outline: none;
            border-color: #00ff41;
            box-shadow: 0 0 30px rgba(0, 255, 65, 0.5);
        }

        select option {
            background: #1a1a2e;
            color: #00ff41;
        }

        code {
            background: rgba(0, 255, 65, 0.1);
            color: #00ff41;
            padding: 2px 6px;
            border-radius: 4px;
            border: 1px solid #00ff41;
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>⚡ LiteLM Forge Dashboard</h1>
            <p>AI Code Generation Testing & Benchmarking Platform</p>
            <div class="controls">
                <button class="btn-primary" onclick="loadData()">🔄 Refresh</button>
                <button class="btn-secondary" onclick="downloadReport()">📥 Download Report</button>
            </div>
        </div>

        <!-- Navigation Tabs -->
        <div class="nav-tabs">
            <button class="nav-tab active" onclick="switchPage('page1')">📊 Dashboard</button>
            <button class="nav-tab" onclick="switchPage('page2')">🤖 Models</button>
            <button class="nav-tab" onclick="switchPage('page3')">📋 Report</button>
            <button class="nav-tab" onclick="switchPage('page4')">🔬 Analysis</button>
        </div>

        <!-- Content -->
        <div class="content">
            <!-- PAGE 1: DASHBOARD -->
            <div id="page1" class="page active">
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
                        <h3>📈 Avg Score</h3>
                        <div class="value" id="avgScore">0/10</div>
                        <div class="label">Code quality score</div>
                    </div>
                    <div class="card">
                        <h3>🤖 Sessions</h3>
                        <div class="value" id="sessionCount">0</div>
                        <div class="label">Testing runs</div>
                    </div>
                </div>

                <div class="info-section">
                    <div class="info-title">📌 About LiteLM Forge</div>
                    <div class="info-content">
                        A complete testing and benchmarking framework for evaluating code generated by local LLMs. Tests models on 14+ coding tasks, executes generated code, and analyzes quality using AI judge models.
                    </div>
                </div>

                <!-- Charts -->
                <div class="chart-container" id="chartsContainer" style="display: none;">
                    <h3>📊 Performance by Prompt</h3>
                    <div class="bar-chart" id="promptChart"></div>
                </div>
            </div>

            <!-- PAGE 2: MODELS -->
            <div id="page2" class="page">
                <h2 style="color: #00ff41; margin-bottom: 20px; font-size: 1.5em; text-shadow: 0 0 10px rgba(0, 255, 65, 0.5);">All Tested Models</h2>
                <div class="models-grid" id="modelsGrid">
                    <!-- Models will be generated from data -->
                </div>
            </div>

            <!-- PAGE 3: REPORT -->
            <div id="page3" class="page">
                <div class="table-container">
                    <h3>Latest Test Results</h3>
                    <table id="resultsTable">
                        <thead>
                            <tr>
                                <th>Prompt</th>
                                <th>Model</th>
                                <th>Status</th>
                                <th>Return Code</th>
                                <th>Time</th>
                            </tr>
                        </thead>
                        <tbody id="resultsBody">
                            <tr><td colspan="5" class="no-data">No data yet</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- PAGE 4: ANALYSIS -->
            <div id="page4" class="page">
                <div class="analysis-section">
                    <h2 style="color: #00ff41; margin-bottom: 20px; font-size: 1.5em; text-shadow: 0 0 10px rgba(0, 255, 65, 0.5);">Code Quality Analysis</h2>
                    
                    <label class="select-label">Select Model to Analyze</label>
                    <select onchange="updateAnalysis(this.value)">
                        <option value="">Choose a model...</option>
                        <option value="all">All Models</option>
                    </select>

                    <div id="analysisContent" style="display: none;">
                        <div class="analysis-grid">
                            <div class="analysis-card">
                                <div class="analysis-metric">Total Analyzed</div>
                                <div class="analysis-value" id="totalVal">0</div>
                            </div>
                            <div class="analysis-card">
                                <div class="analysis-metric">Average Score</div>
                                <div class="analysis-value" id="avgScoreVal">0/10</div>
                            </div>
                            <div class="analysis-card">
                                <div class="analysis-metric">Pass Rate</div>
                                <div class="analysis-value" id="passRateVal">0%</div>
                            </div>
                        </div>

                        <div class="table-container">
                            <h3>Performance by Prompt</h3>
                            <table>
                                <thead>
                                    <tr>
                                        <th>Prompt</th>
                                        <th>Score</th>
                                        <th>Status</th>
                                    </tr>
                                </thead>
                                <tbody id="promptDetails">
                                    <tr><td colspan="3" class="no-data">No data</td></tr>
                                </tbody>
                            </table>
                        </div>
                    </div>

                    <div id="emptyState" class="info-section" style="text-align: center; color: #888;">
                        Select a model to view analysis metrics
                    </div>
                </div>

                <div class="table-container">
                    <h3>Code Quality Analysis Details</h3>
                    <table id="analysisTable">
                        <thead>
                            <tr>
                                <th>Prompt</th>
                                <th>Model</th>
                                <th>Score</th>
                                <th>Status</th>
                                <th>Verdict</th>
                            </tr>
                        </thead>
                        <tbody id="analysisBody">
                            <tr><td colspan="5" class="no-data">No analyses yet</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- Refresh time -->
        <div class="refresh-time" id="refreshTime"></div>
    </div>

    <script>
        let reportData = null;
        let analysisData = null;

        async function loadData() {
            try {
                // Fetch from API endpoints
                const reportRes = await fetch('/api/report');
                const analysisRes = await fetch('/api/analysis');
                
                if (reportRes.ok) {
                    reportData = await reportRes.json();
                } else {
                    reportData = { sessions: [] };
                }
                
                if (analysisRes.ok) {
                    analysisData = await analysisRes.json();
                } else {
                    analysisData = { analyses: [], summary: {} };
                }

                updateDashboard();
                document.getElementById('refreshTime').textContent = `Last updated: ${new Date().toLocaleTimeString()}`;
            } catch (error) {
                console.error('Error loading data:', error);
                document.getElementById('refreshTime').textContent = `Error loading data: ${error.message}`;
            }
        }

        function updateDashboard() {
            if (!reportData || !reportData.sessions) return;

            let totalTests = 0;
            let passedTests = 0;
            const allResults = [];
            const modelMap = {};

            reportData.sessions.forEach(session => {
                const modelName = session.model_name;
                if (!modelMap[modelName]) {
                    modelMap[modelName] = {
                        name: modelName,
                        total: 0,
                        passed: 0,
                        source: 'Local LM',
                        results: []
                    };
                }

                session.results.forEach(result => {
                    allResults.push(result);
                    totalTests++;
                    if (result.passed) passedTests++;
                    modelMap[modelName].total++;
                    if (result.passed) modelMap[modelName].passed++;
                    modelMap[modelName].results.push(result);
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
            document.getElementById('avgScore').textContent = avgScore + '/10';
            document.getElementById('sessionCount').textContent = reportData.sessions.length;

            updateResultsTable(allResults);
            updateModelsPage(modelMap);
            
            if (analysisData.analyses) {
                updateAnalysisTable(analysisData.analyses);
                populateModelSelect(modelMap);
            }

            if (analysisData.summary && analysisData.summary.by_prompt) {
                updateCharts();
                document.getElementById('chartsContainer').style.display = 'block';
            }
        }

        function updateModelsPage(modelMap) {
            const grid = document.getElementById('modelsGrid');
            const models = Object.values(modelMap);

            if (models.length === 0) {
                grid.innerHTML = '<div class="no-data">No models tested yet</div>';
                return;
            }

            grid.innerHTML = models.map((model, idx) => `
                <div class="model-card" onclick="selectModel(this)">
                    <div class="model-name">${model.name}</div>
                    <div class="model-meta">
                        <div><span>Source:</span> <span>${model.source}</span></div>
                        <div><span>Tests:</span> <span>${model.total}</span></div>
                    </div>
                    <div class="model-stats">
                        <div class="stat-box">
                            <div class="stat-num">${model.total}</div>
                            <div class="stat-label">Prompts</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-num">${model.passed}/${model.total}</div>
                            <div class="stat-label">Passed</div>
                        </div>
                    </div>
                    <div class="keywords">
                        <div class="keyword-label">Status</div>
                        <div class="keyword-list">
                            <span class="keyword-tag good">Active</span>
                            <span class="keyword-tag">${Math.round((model.passed/model.total)*100)}%</span>
                        </div>
                    </div>
                </div>
            `).join('');
        }

        function selectModel(element) {
            document.querySelectorAll('.model-card').forEach(c => c.classList.remove('selected'));
            element.classList.add('selected');
        }

        function populateModelSelect(modelMap) {
            const select = document.querySelector('select');
            const models = Object.values(modelMap);
            
            // Clear existing options (keep first two)
            while (select.options.length > 2) {
                select.remove(2);
            }
            
            models.forEach(model => {
                if (!Array.from(select.options).find(o => o.value === model.name)) {
                    const option = document.createElement('option');
                    option.value = model.name;
                    option.textContent = model.name;
                    select.appendChild(option);
                }
            });
        }

        function updateResultsTable(results) {
            const tbody = document.getElementById('resultsBody');
            
            if (results.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" class="no-data">No test results yet</td></tr>';
                return;
            }

            tbody.innerHTML = results.slice(-20).reverse().map(result => {
                const status = result.passed 
                    ? '<span class="badge badge-pass">✅ Passed</span>'
                    : '<span class="badge badge-fail">❌ Failed</span>';
                
                const time = result.timestamp 
                    ? new Date(result.timestamp).toLocaleTimeString()
                    : 'N/A';

                return `
                    <tr>
                        <td><strong>${result.prompt_name}</strong></td>
                        <td>${result.model_name}</td>
                        <td>${status}</td>
                        <td><code>${result.return_code}</code></td>
                        <td>${time}</td>
                    </tr>
                `;
            }).join('');
        }

        function updateAnalysisTable(analyses) {
            const tbody = document.getElementById('analysisBody');
            
            if (analyses.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" class="no-data">No analyses yet</td></tr>';
                return;
            }

            tbody.innerHTML = analyses.slice(-20).reverse().map(analysis => {
                const score = analysis.overall_score || 0;
                const scoreClass = score >= 7 ? 'high' : score >= 4 ? 'medium' : 'low';
                const status = analysis.passed 
                    ? '<span class="badge badge-pass">✅</span>'
                    : '<span class="badge badge-warning">⚠️</span>';

                return `
                    <tr>
                        <td><strong>${analysis.prompt_name}</strong></td>
                        <td>${analysis.model_name}</td>
                        <td><span class="score ${scoreClass}">${score}/10</span></td>
                        <td>${status}</td>
                        <td>${analysis.verdict || 'N/A'}</td>
                    </tr>
                `;
            }).join('');
        }

        function updateCharts() {
            const chart = document.getElementById('promptChart');
            const summary = analysisData.summary;

            if (!summary.by_prompt) return;

            chart.innerHTML = Object.entries(summary.by_prompt).map(([prompt, stats]) => {
                const width = (stats.avg_score / 10) * 100;
                return `
                    <div class="bar-item">
                        <div class="bar-label">${prompt}</div>
                        <div class="bar-background">
                            <div class="bar-fill" style="width: ${width}%">
                                ${stats.avg_score.toFixed(1)}/10
                            </div>
                        </div>
                    </div>
                `;
            }).join('');
        }

        function updateAnalysis(modelKey) {
            const content = document.getElementById('analysisContent');
            const empty = document.getElementById('emptyState');
            
            if (!modelKey) {
                content.style.display = 'none';
                empty.style.display = 'block';
                return;
            }

            content.style.display = 'block';
            empty.style.display = 'none';

            let filtered = analysisData.analyses;
            if (modelKey !== 'all') {
                filtered = analysisData.analyses.filter(a => a.model_name === modelKey);
            }

            if (filtered.length === 0) {
                document.getElementById('promptDetails').innerHTML = '<tr><td colspan="3" class="no-data">No analyses for this model</td></tr>';
                document.getElementById('totalVal').textContent = '0';
                document.getElementById('avgScoreVal').textContent = '0/10';
                document.getElementById('passRateVal').textContent = '0%';
                return;
            }

            const passed = filtered.filter(a => a.passed).length;
            const scores = filtered.map(a => a.overall_score || 0).filter(s => s > 0);
            const avgScore = scores.length > 0 ? (scores.reduce((a, b) => a + b, 0) / scores.length).toFixed(1) : 0;
            const passRate = Math.round((passed / filtered.length) * 100);

            document.getElementById('totalVal').textContent = filtered.length;
            document.getElementById('avgScoreVal').textContent = avgScore + '/10';
            document.getElementById('passRateVal').textContent = passRate + '%';

            const promptHtml = filtered.map(a => `
                <tr>
                    <td><strong>${a.prompt_name}</strong></td>
                    <td><span class="score ${a.overall_score >= 7 ? 'high' : a.overall_score >= 4 ? 'medium' : 'low'}">${a.overall_score}/10</span></td>
                    <td><span class="badge ${a.passed ? 'badge-pass' : 'badge-warning'}">${a.passed ? '✅ Pass' : '⚠️ Fail'}</span></td>
                </tr>
            `).join('');

            document.getElementById('promptDetails').innerHTML = promptHtml;
        }

        function switchPage(pageId) {
            document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
            document.getElementById(pageId).classList.add('active');
            
            document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
            event.target.classList.add('active');
        }

        function downloadReport() {
            const data = {
                report: reportData,
                analysis: analysisData,
                generated: new Date().toISOString()
            };

            const json = JSON.stringify(data, null, 2);
            const blob = new Blob([json], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `litelm-report-${new Date().getTime()}.json`;
            a.click();
        }

        // Load data on page load
        loadData();
        
        // Auto-refresh every 5 seconds
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
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(DASHBOARD_HTML.encode('utf-8'))
        
        elif self.path == "/api/report":
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            
            try:
                with open(REPORT_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
            except FileNotFoundError:
                self.wfile.write(json.dumps({"sessions": []}).encode('utf-8'))
        
        elif self.path == "/api/analysis":
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            
            try:
                with open(ANALYSIS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
            except FileNotFoundError:
                self.wfile.write(json.dumps({"analyses": [], "summary": {}}).encode('utf-8'))
        
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