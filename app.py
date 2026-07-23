"""
Open Telekom Cloud Control & ECS Diagnostic Suite.
A lightweight, zero-dependency Python web application for container health monitoring,
ALB Target Group validation, CPU stress testing, and environment variable inspection.
"""

import datetime
import json
import os
import platform
import socket
import sys
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

START_TIME = time.time()

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Open Telekom Cloud Control & ECS Tester</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    fontFamily: {
                        sans: ['Inter', 'sans-serif'],
                        mono: ['JetBrains Mono', 'monospace']
                    },
                    colors: {
                        brand: {
                            500: '#2563eb',
                            600: '#1d4ed8',
                            700: '#1e40af'
                        }
                    }
                }
            }
        }
    </script>
    <style>
        .glass-panel {
            background: rgba(15, 23, 42, 0.85);
            border: 1px solid rgba(255, 255, 255, 0.08);
        }
        .tab-btn.active {
            border-bottom: 2px solid #2563eb;
            color: #ffffff;
            font-weight: 600;
        }
    </style>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen flex flex-col font-sans selection:bg-blue-600 selection:text-white">

    <!-- Top Navigation Header -->
    <header class="bg-slate-900 border-b border-slate-800 sticky top-0 z-50 px-4 md:px-8 py-3.5 flex justify-between items-center shadow-xl">
        <div class="flex items-center space-x-3">
            <div class="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center font-bold text-sm text-white font-mono">
                OTC
            </div>
            <div>
                <div class="flex items-center space-x-2">
                    <span class="font-bold text-lg md:text-xl tracking-tight text-white">Cloud Control Console</span>
                    <span class="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-mono border border-slate-700">v2.0</span>
                </div>
                <p class="text-xs text-slate-400 font-medium hidden sm:block">Open Telekom Cloud Container Diagnostic Suite</p>
            </div>
        </div>

        <div class="flex items-center space-x-4">
            <div class="hidden md:flex items-center space-x-2 bg-slate-800 px-3 py-1.5 rounded border border-slate-700 text-xs">
                <span class="text-slate-400">Uptime:</span>
                <span id="live-uptime" class="font-mono text-emerald-400 font-semibold">__UPTIME__s</span>
            </div>
            <div class="flex items-center space-x-2 bg-emerald-500/10 border border-emerald-500/30 px-3 py-1.5 rounded-full">
                <span class="inline-block w-2 h-2 rounded-full bg-emerald-500"></span>
                <span class="text-xs font-semibold text-emerald-400">Status: Healthy</span>
            </div>
        </div>
    </header>

    <!-- Main Container -->
    <main class="max-w-6xl mx-auto px-4 md:px-8 py-8 w-full flex-grow">
        
        <!-- Hero Card -->
        <div class="rounded-xl bg-slate-900 border border-slate-800 p-6 md:p-8 mb-8 shadow-xl">
            <div class="flex flex-col md:flex-row justify-between md:items-center gap-6">
                <div>
                    <div class="inline-flex items-center gap-2 px-2.5 py-1 rounded bg-slate-800 border border-slate-700 text-xs text-slate-300 font-mono mb-3">
                        <span>Open Telekom Cloud</span>
                        <span class="text-slate-600">/</span>
                        <span>ECS Container Engine</span>
                    </div>
                    <h1 class="text-2xl md:text-3xl font-bold tracking-tight text-white mb-2">
                        ECS Container Dashboard & Diagnostic Suite
                    </h1>
                    <p class="text-slate-400 text-sm max-w-2xl">
                        Bereitgestellt in Docker auf Open Telekom Cloud ECS. Nutzen Sie diese Konsole zur Überprüfung von Health Checks, Auto-Scaling, Failover-Verhalten und Container-Metadaten.
                    </p>
                </div>
                <div class="flex flex-wrap gap-2 sm:self-start md:self-center">
                    <button onclick="switchTab('devops')" class="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-sm font-semibold rounded transition shadow flex items-center gap-2">
                        <span>Diagnostic Console</span>
                    </button>
                    <a href="/health" target="_blank" class="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-sm font-semibold rounded border border-slate-700 transition flex items-center gap-2">
                        <span>/health Endpoint</span>
                    </a>
                </div>
            </div>
        </div>

        <!-- Metric Stat Grid -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            
            <div class="glass-panel p-5 rounded-xl border border-slate-800">
                <div class="text-xs uppercase tracking-wider text-slate-400 font-semibold mb-1">Server Zeit</div>
                <div id="live-clock" class="text-lg font-bold text-white font-mono">__NOW__</div>
                <div class="text-xs text-slate-500 mt-2">Container Local Time</div>
            </div>

            <div class="glass-panel p-5 rounded-xl border border-slate-800">
                <div class="text-xs uppercase tracking-wider text-slate-400 font-semibold mb-1">Container Hostname</div>
                <div class="text-lg font-bold text-amber-400 font-mono truncate" title="__HOSTNAME__">__HOSTNAME__</div>
                <div class="text-xs text-slate-500 mt-2">ECS Task Container ID</div>
            </div>

            <div class="glass-panel p-5 rounded-xl border border-slate-800">
                <div class="text-xs uppercase tracking-wider text-slate-400 font-semibold mb-1">Client IP-Adresse</div>
                <div class="text-lg font-bold text-cyan-400 font-mono">__CLIENT_IP__</div>
                <div class="text-xs text-slate-500 mt-2">Request Origin Address</div>
            </div>

            <div class="glass-panel p-5 rounded-xl border border-slate-800">
                <div class="text-xs uppercase tracking-wider text-slate-400 font-semibold mb-1">Prozess Laufzeit</div>
                <div id="uptime-counter" class="text-lg font-bold text-emerald-400 font-mono">__UPTIME__s</div>
                <div class="text-xs text-slate-500 mt-2">Active Execution Time</div>
            </div>

        </div>

        <!-- Navigation Tabs -->
        <div class="border-b border-slate-800 mb-6 flex space-x-6">
            <button onclick="switchTab('overview')" id="tab-btn-overview" class="tab-btn active pb-3 text-sm text-slate-400 hover:text-white transition">
                System Übersicht
            </button>
            <button onclick="switchTab('devops')" id="tab-btn-devops" class="tab-btn pb-3 text-sm text-slate-400 hover:text-white transition">
                DevOps & Diagnostic Tests
            </button>
            <button onclick="switchTab('api')" id="tab-btn-api" class="tab-btn pb-3 text-sm text-slate-400 hover:text-white transition">
                REST API Referenz
            </button>
        </div>

        <!-- Tab 1: Overview -->
        <div id="tab-overview" class="tab-content space-y-6">
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                <!-- Stack info -->
                <div class="glass-panel rounded-xl p-6 md:col-span-2 border border-slate-800">
                    <h3 class="text-base font-bold text-white mb-4">
                        System- & Infrastruktur-Spezifikationen
                    </h3>
                    <div class="grid grid-cols-2 sm:grid-cols-3 gap-4">
                        <div class="bg-slate-900 border border-slate-800 p-3.5 rounded-lg">
                            <span class="text-xs text-slate-400 font-medium block">Python Version</span>
                            <span class="text-sm font-semibold text-slate-200 font-mono">__PYTHON_VERSION__</span>
                        </div>
                        <div class="bg-slate-900 border border-slate-800 p-3.5 rounded-lg">
                            <span class="text-xs text-slate-400 font-medium block">Betriebssystem</span>
                            <span class="text-sm font-semibold text-slate-200 font-mono">__SYSTEM_OS__</span>
                        </div>
                        <div class="bg-slate-900 border border-slate-800 p-3.5 rounded-lg">
                            <span class="text-xs text-slate-400 font-medium block">CPU Kerne</span>
                            <span class="text-sm font-semibold text-slate-200 font-mono">__CPU_COUNT__ vCPU</span>
                        </div>
                        <div class="bg-slate-900 border border-slate-800 p-3.5 rounded-lg">
                            <span class="text-xs text-slate-400 font-medium block">Listen Port</span>
                            <span class="text-sm font-semibold text-slate-200 font-mono">8080</span>
                        </div>
                        <div class="bg-slate-900 border border-slate-800 p-3.5 rounded-lg">
                            <span class="text-xs text-slate-400 font-medium block">CI/CD Pipeline</span>
                            <span class="text-sm font-semibold text-emerald-400 font-mono">GitHub Actions</span>
                        </div>
                        <div class="bg-slate-900 border border-slate-800 p-3.5 rounded-lg">
                            <span class="text-xs text-slate-400 font-medium block">Cloud Ziel</span>
                            <span class="text-sm font-semibold text-blue-600 font-mono">OTC ECS</span>
                        </div>
                    </div>
                </div>

                <!-- Active Stack Badges -->
                <div class="glass-panel rounded-xl p-6 border border-slate-800 flex flex-col justify-between">
                    <div>
                        <h3 class="text-base font-bold text-white mb-3">Aktive Komponenten</h3>
                        <p class="text-xs text-slate-400 mb-4">Übersicht der konfigurierten Container-Module.</p>
                        <div class="flex flex-wrap gap-2">
                            <span class="bg-slate-800 text-slate-300 text-xs px-2.5 py-1 rounded border border-slate-700 font-mono">Open Telekom Cloud</span>
                            <span class="bg-slate-800 text-slate-300 text-xs px-2.5 py-1 rounded border border-slate-700 font-mono">Docker Container</span>
                            <span class="bg-slate-800 text-slate-300 text-xs px-2.5 py-1 rounded border border-slate-700 font-mono">Python 3.9 Standard</span>
                            <span class="bg-slate-800 text-slate-300 text-xs px-2.5 py-1 rounded border border-slate-700 font-mono">Tailwind CSS</span>
                            <span class="bg-slate-800 text-slate-300 text-xs px-2.5 py-1 rounded border border-slate-700 font-mono">ALB Ready</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Tab 2: DevOps & Cloud Test Console -->
        <div id="tab-devops" class="tab-content hidden space-y-6">
            <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
                <!-- Action Controls -->
                <div class="lg:col-span-5 space-y-3">
                    <h3 class="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">Test-Aktionen</h3>
                    
                    <button onclick="runTest('/api/health')" class="w-full text-left p-4 rounded-lg glass-panel hover:bg-slate-800/80 transition border border-slate-800 flex items-center justify-between group">
                        <div>
                            <div class="font-semibold text-white group-hover:text-emerald-400 transition">
                                Container Health Check
                            </div>
                            <div class="text-xs text-slate-400 mt-1">Prüft GET /health für ALB Target Groups</div>
                        </div>
                        <span class="text-xs px-2 py-1 rounded bg-slate-800 text-slate-300 font-mono border border-slate-700">GET /health</span>
                    </button>

                    <button onclick="runTest('/api/load')" class="w-full text-left p-4 rounded-lg glass-panel hover:bg-slate-800/80 transition border border-slate-800 flex items-center justify-between group">
                        <div>
                            <div class="font-semibold text-white group-hover:text-amber-400 transition">
                                CPU-Stresstest simulieren
                            </div>
                            <div class="text-xs text-slate-400 mt-1">Erzeugt 3s CPU-Last für Auto-Scaling</div>
                        </div>
                        <span class="text-xs px-2 py-1 rounded bg-slate-800 text-slate-300 font-mono border border-slate-700">GET /api/load</span>
                    </button>

                    <button onclick="runTest('/api/error')" class="w-full text-left p-4 rounded-lg glass-panel hover:bg-slate-800/80 transition border border-slate-800 flex items-center justify-between group">
                        <div>
                            <div class="font-semibold text-white group-hover:text-rose-400 transition">
                                HTTP 500 Fehler simulieren
                            </div>
                            <div class="text-xs text-slate-400 mt-1">Prüft ALB Failover & Resiliency</div>
                        </div>
                        <span class="text-xs px-2 py-1 rounded bg-slate-800 text-slate-300 font-mono border border-slate-700">GET /api/error</span>
                    </button>

                    <button onclick="runTest('/api/env')" class="w-full text-left p-4 rounded-lg glass-panel hover:bg-slate-800/80 transition border border-slate-800 flex items-center justify-between group">
                        <div>
                            <div class="font-semibold text-white group-hover:text-cyan-400 transition">
                                Environment Variablen
                            </div>
                            <div class="text-xs text-slate-400 mt-1">Liest Container Parameter aus</div>
                        </div>
                        <span class="text-xs px-2 py-1 rounded bg-slate-800 text-slate-300 font-mono border border-slate-700">GET /api/env</span>
                    </button>

                    <button onclick="runTest('/api/headers')" class="w-full text-left p-4 rounded-lg glass-panel hover:bg-slate-800/80 transition border border-slate-800 flex items-center justify-between group">
                        <div>
                            <div class="font-semibold text-white group-hover:text-purple-400 transition">
                                HTTP Request Header
                            </div>
                            <div class="text-xs text-slate-400 mt-1">Inspektion von Proxy & SSL Headern</div>
                        </div>
                        <span class="text-xs px-2 py-1 rounded bg-slate-800 text-slate-300 font-mono border border-slate-700">GET /api/headers</span>
                    </button>
                </div>

                <!-- Response Console -->
                <div class="lg:col-span-7 flex flex-col">
                    <div class="flex justify-between items-center mb-2">
                        <span class="text-xs font-bold uppercase tracking-wider text-slate-400">Live API Konsole</span>
                        <span id="response-status" class="text-xs font-mono font-semibold px-2.5 py-1 rounded bg-slate-800 text-slate-400 border border-slate-700">Bereit</span>
                    </div>
                    
                    <div class="glass-panel rounded-xl p-4 flex-grow flex flex-col font-mono text-xs overflow-hidden border border-slate-800 min-h-[350px]">
                        <div class="flex items-center justify-between pb-3 border-b border-slate-800 text-slate-400">
                            <span id="console-endpoint">Wähle eine Aktion aus...</span>
                            <span id="console-time" class="text-slate-500">-- ms</span>
                        </div>
                        <pre id="console-output" class="p-3 text-emerald-400 overflow-x-auto whitespace-pre-wrap flex-grow font-mono leading-relaxed">// Antwortergebnisse werden hier angezeigt...</pre>
                    </div>
                </div>
            </div>
        </div>

        <!-- Tab 3: API Explorer -->
        <div id="tab-api" class="tab-content hidden space-y-6">
            <div class="glass-panel rounded-xl overflow-hidden border border-slate-800">
                <div class="p-6 border-b border-slate-800">
                    <h3 class="text-lg font-bold text-white">API Endpunkte</h3>
                    <p class="text-xs text-slate-400 mt-1">Schnittstellenreferenz der Anwendung.</p>
                </div>

                <div class="overflow-x-auto">
                    <table class="w-full text-left text-sm text-slate-300">
                        <thead class="bg-slate-900 text-xs uppercase tracking-wider text-slate-400 border-b border-slate-800">
                            <tr>
                                <th class="p-4">Methode</th>
                                <th class="p-4">Endpoint</th>
                                <th class="p-4">Beschreibung</th>
                                <th class="p-4">Einsatzbereich</th>
                                <th class="p-4 text-right">Aktion</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-slate-800 font-mono text-xs">
                            <tr class="hover:bg-slate-900/40">
                                <td class="p-4"><span class="px-2 py-0.5 rounded bg-slate-800 text-blue-400 border border-slate-700">GET</span></td>
                                <td class="p-4 font-bold text-white">/health</td>
                                <td class="p-4 text-slate-400">Health Check Status & Uptime</td>
                                <td class="p-4 text-emerald-400">ALB Target Groups</td>
                                <td class="p-4 text-right"><a href="/health" target="_blank" class="text-blue-600 hover:underline">Aufrufen</a></td>
                            </tr>
                            <tr class="hover:bg-slate-900/40">
                                <td class="p-4"><span class="px-2 py-0.5 rounded bg-slate-800 text-blue-400 border border-slate-700">GET</span></td>
                                <td class="p-4 font-bold text-white">/api/metrics</td>
                                <td class="p-4 text-slate-400">Container & OS Metriken</td>
                                <td class="p-4 text-cyan-400">System Monitoring</td>
                                <td class="p-4 text-right"><a href="/api/metrics" target="_blank" class="text-blue-600 hover:underline">Aufrufen</a></td>
                            </tr>
                            <tr class="hover:bg-slate-900/40">
                                <td class="p-4"><span class="px-2 py-0.5 rounded bg-slate-800 text-blue-400 border border-slate-700">GET</span></td>
                                <td class="p-4 font-bold text-white">/api/load</td>
                                <td class="p-4 text-slate-400">Simuliert CPU-Last (3s)</td>
                                <td class="p-4 text-amber-400">Auto-Scaling Tests</td>
                                <td class="p-4 text-right"><a href="/api/load" target="_blank" class="text-blue-600 hover:underline">Aufrufen</a></td>
                            </tr>
                            <tr class="hover:bg-slate-900/40">
                                <td class="p-4"><span class="px-2 py-0.5 rounded bg-slate-800 text-blue-400 border border-slate-700">GET</span></td>
                                <td class="p-4 font-bold text-white">/api/error</td>
                                <td class="p-4 text-slate-400">Simuliert HTTP 500 Fehler</td>
                                <td class="p-4 text-rose-400">Failover Testing</td>
                                <td class="p-4 text-right"><a href="/api/error" target="_blank" class="text-blue-600 hover:underline">Aufrufen</a></td>
                            </tr>
                            <tr class="hover:bg-slate-900/40">
                                <td class="p-4"><span class="px-2 py-0.5 rounded bg-slate-800 text-blue-400 border border-slate-700">GET</span></td>
                                <td class="p-4 font-bold text-white">/api/env</td>
                                <td class="p-4 text-slate-400">Liest Environment Variablen aus</td>
                                <td class="p-4 text-purple-400">Parameter Audit</td>
                                <td class="p-4 text-right"><a href="/api/env" target="_blank" class="text-blue-600 hover:underline">Aufrufen</a></td>
                            </tr>
                            <tr class="hover:bg-slate-900/40">
                                <td class="p-4"><span class="px-2 py-0.5 rounded bg-slate-800 text-blue-400 border border-slate-700">GET</span></td>
                                <td class="p-4 font-bold text-white">/api/headers</td>
                                <td class="p-4 text-slate-400">Liest Request Header aus</td>
                                <td class="p-4 text-indigo-400">Proxy Inspection</td>
                                <td class="p-4 text-right"><a href="/api/headers" target="_blank" class="text-blue-600 hover:underline">Aufrufen</a></td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

    </main>

    <!-- Footer -->
    <footer class="bg-slate-900 border-t border-slate-800 text-center py-5 px-4 text-xs text-slate-400">
        <div class="max-w-6xl mx-auto flex flex-col items-center justify-center gap-2">
            <div class="flex flex-col sm:flex-row items-center justify-center gap-2 sm:gap-4">
                <span>Open Telekom Cloud | ECS Container Application</span>
                <span class="hidden sm:inline text-slate-600">•</span>
                <span class="font-mono text-slate-500">Port 8080 | Python 3.9</span>
            </div>
            <div class="text-slate-400 text-xs font-medium pt-1">
                Projekt von <span class="text-white font-semibold">Antonio</span> | GitHub: <a href="https://github.com/ant0ni014" target="_blank" rel="noopener noreferrer" class="text-blue-600 hover:text-blue-400 font-mono underline transition">github.com/ant0ni014</a>
            </div>
        </div>
    </footer>

    <!-- Interactive Scripting -->
    <script>
        let startTime = Date.now() - (__UPTIME__ * 1000);

        function updateClockAndUptime() {
            const now = new Date();
            const dateStr = now.toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' });
            const timeStr = now.toLocaleTimeString('de-DE');
            document.getElementById('live-clock').innerText = dateStr + ' - ' + timeStr;

            const elapsedSec = Math.floor((Date.now() - startTime) / 1000);
            document.getElementById('live-uptime').innerText = elapsedSec + 's';
            document.getElementById('uptime-counter').innerText = elapsedSec + 's';
        }

        setInterval(updateClockAndUptime, 1000);

        function switchTab(tabId) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
            document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));

            document.getElementById('tab-' + tabId).classList.remove('hidden');
            document.getElementById('tab-btn-' + tabId).classList.add('active');
        }

        async function runTest(endpoint) {
            const output = document.getElementById('console-output');
            const endpointLabel = document.getElementById('console-endpoint');
            const timeLabel = document.getElementById('console-time');
            const statusLabel = document.getElementById('response-status');

            endpointLabel.innerText = 'GET ' + endpoint;
            output.innerText = '// Sende HTTP Request...';
            statusLabel.innerText = 'Pending...';
            statusLabel.className = 'text-xs font-mono font-semibold px-2.5 py-1 rounded bg-amber-900/50 text-amber-300 border border-amber-700';

            const start = performance.now();
            try {
                const res = await fetch(endpoint);
                const duration = Math.round(performance.now() - start);
                const data = await res.json();

                timeLabel.innerText = duration + ' ms';
                statusLabel.innerText = res.status + ' ' + res.statusText;

                if (res.ok) {
                    statusLabel.className = 'text-xs font-mono font-semibold px-2.5 py-1 rounded bg-emerald-900/50 text-emerald-300 border border-emerald-700';
                    output.className = 'p-3 text-emerald-400 overflow-x-auto whitespace-pre-wrap flex-grow font-mono leading-relaxed';
                } else {
                    statusLabel.className = 'text-xs font-mono font-semibold px-2.5 py-1 rounded bg-rose-900/50 text-rose-300 border border-rose-700';
                    output.className = 'p-3 text-rose-400 overflow-x-auto whitespace-pre-wrap flex-grow font-mono leading-relaxed';
                }

                output.innerText = JSON.stringify(data, null, 2);
            } catch (err) {
                const duration = Math.round(performance.now() - start);
                timeLabel.innerText = duration + ' ms';
                statusLabel.innerText = 'FETCH ERROR';
                statusLabel.className = 'text-xs font-mono font-semibold px-2.5 py-1 rounded bg-rose-900/50 text-rose-300 border border-rose-700';
                output.className = 'p-3 text-rose-400 overflow-x-auto whitespace-pre-wrap flex-grow font-mono leading-relaxed';
                output.innerText = '// Fehler beim Aufruf: ' + err.message;
            }
        }
    </script>
</body>
</html>
"""

class CloudDashboardHandler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {self.address_string()} - {format % args}")

    def send_json_response(self, data, status_code=200):
        response_bytes = json.dumps(data, indent=2, ensure_ascii=False).encode('utf-8')
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Length', str(len(response_bytes)))
        self.end_headers()
        self.wfile.write(response_bytes)

    def do_GET(self):
        path = self.path.split('?')[0].rstrip('/')

        if path in ('', '/index.html'):
            self.handle_dashboard()
        elif path in ('/health', '/api/health'):
            self.handle_health()
        elif path == '/api/metrics':
            self.handle_metrics()
        elif path == '/api/load':
            self.handle_load_simulation()
        elif path == '/api/error':
            self.handle_error_simulation()
        elif path == '/api/env':
            self.handle_env()
        elif path == '/api/headers':
            self.handle_headers()
        else:
            self.send_json_response({
                "error": "Not Found",
                "path": self.path,
                "available_endpoints": [
                    "/",
                    "/health",
                    "/api/metrics",
                    "/api/load",
                    "/api/error",
                    "/api/env",
                    "/api/headers"
                ]
            }, 404)

    def handle_health(self):
        uptime = int(time.time() - START_TIME)
        data = {
            "status": "UP",
            "service": "otc-ecs-cloud-app",
            "hostname": socket.gethostname(),
            "uptime_seconds": uptime,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }
        self.send_json_response(data, 200)

    def handle_metrics(self):
        uptime = int(time.time() - START_TIME)
        data = {
            "service": "otc-ecs-cloud-app",
            "hostname": socket.gethostname(),
            "client_ip": self.client_address[0],
            "uptime_seconds": uptime,
            "python_version": platform.python_version(),
            "system_os": f"{platform.system()} {platform.release()}",
            "cpu_count": os.cpu_count() or 1,
            "environment_vars_count": len(os.environ),
            "timestamp": datetime.datetime.now().strftime("%d.%m.%Y - %H:%M:%S")
        }
        self.send_json_response(data, 200)

    def handle_load_simulation(self):
        start = time.time()
        duration = 3.0
        iterations = 0
        while time.time() - start < duration:
            _ = [x**2 for x in range(5000)]
            iterations += 1

        elapsed = round(time.time() - start, 3)
        self.send_json_response({
            "status": "success",
            "action": "cpu_load_simulation",
            "duration_seconds": elapsed,
            "iterations_completed": iterations,
            "message": f"CPU load simulation completed successfully in {elapsed} seconds."
        }, 200)

    def handle_error_simulation(self):
        self.send_json_response({
            "status": "error",
            "code": 500,
            "message": "Simulated 500 Internal Server Error for testing ECS failover and ALB health checks.",
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }, 500)

    def handle_env(self):
        safe_env = {}
        sensitive_keywords = ["PASS", "SECRET", "TOKEN", "KEY", "AUTH", "CREDENTIAL"]
        for k, v in os.environ.items():
            if any(s in k.upper() for s in sensitive_keywords):
                safe_env[k] = "******** [MASKED FOR SECURITY]"
            else:
                safe_env[k] = v

        self.send_json_response({
            "total_count": len(safe_env),
            "environment_variables": safe_env
        }, 200)

    def handle_headers(self):
        headers_dict = {k: v for k, v in self.headers.items()}
        self.send_json_response({
            "client_ip": self.client_address[0],
            "client_port": self.client_address[1],
            "headers": headers_dict
        }, 200)

    def handle_dashboard(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()

        now = datetime.datetime.now().strftime("%d.%m.%Y - %H:%M:%S Uhr")
        hostname = socket.gethostname()
        client_ip = self.client_address[0]
        uptime = int(time.time() - START_TIME)

        html_content = (
            HTML_TEMPLATE
            .replace('__NOW__', now)
            .replace('__HOSTNAME__', hostname)
            .replace('__CLIENT_IP__', client_ip)
            .replace('__UPTIME__', str(uptime))
            .replace('__PYTHON_VERSION__', platform.python_version())
            .replace('__SYSTEM_OS__', platform.system())
            .replace('__CPU_COUNT__', str(os.cpu_count() or 1))
        )

        self.wfile.write(html_content.encode('utf-8'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print("==================================================")
    print(" [INFO] OTC Cloud Control Dashboard Server v2.0")
    print(f" [INFO] Server gestartet auf Port {port}")
    print(f" [INFO] Health Check Route: http://localhost:{port}/health")
    print("==================================================")
    server = HTTPServer(('0.0.0.0', port), CloudDashboardHandler)
    server.serve_forever()