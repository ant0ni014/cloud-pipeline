"""
T Cloud Public - ECS Diagnostics & Health Dashboard.
Enterprise container health monitoring, ALB target group validation, CPU load testing, and deployment inspection.
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
<html lang="de" class="h-full bg-[#090a0f]">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>T Cloud Public — Container Diagnostic Console</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    fontFamily: {
                        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
                        mono: ['JetBrains Mono', 'monospace']
                    },
                    colors: {
                        telekom: {
                            500: '#E20074',
                            600: '#D00069',
                            700: '#B00058'
                        }
                    }
                }
            }
        }
    </script>
    <style>
        body { font-feature-settings: "cv02", "cv03", "cv04", "cv11"; }
        .panel { background-color: #11131c; border: 1px solid #1e2333; }
        .nav-link.active {
            color: #ffffff;
            border-bottom: 2px solid #E20074;
            font-weight: 600;
        }
    </style>
</head>
<body class="text-slate-200 min-h-full flex flex-col font-sans selection:bg-telekom-500 selection:text-white">

    <!-- Top Navigation Header -->
    <header class="bg-[#0e1017] border-b border-[#1e2333] sticky top-0 z-50 px-4 md:px-8 py-3 flex justify-between items-center shadow-md">
        <div class="flex items-center space-x-3">
            <div class="w-8 h-8 rounded bg-telekom-500 flex items-center justify-center font-bold text-base text-white font-mono shadow-sm tracking-tighter">
                T
            </div>
            <div>
                <div class="flex items-center space-x-2">
                    <span class="font-bold text-base md:text-lg tracking-tight text-white">T Cloud Public</span>
                    <span class="text-slate-500 text-sm">/</span>
                    <span class="text-xs font-semibold px-2 py-0.5 rounded bg-[#181c28] text-slate-300 border border-[#272d40]">ECS Console</span>
                </div>
            </div>
        </div>

        <div class="flex items-center space-x-4">
            <div class="hidden sm:flex items-center space-x-2 bg-[#141722] px-3 py-1.5 rounded border border-[#222838] text-xs font-mono">
                <span class="text-slate-400">Uptime:</span>
                <span id="live-uptime" class="text-emerald-400 font-semibold">__UPTIME__s</span>
            </div>
            <div class="flex items-center space-x-2 bg-emerald-950/40 border border-emerald-800/50 px-3 py-1.5 rounded">
                <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                <span class="text-xs font-medium text-emerald-300">Healthy</span>
            </div>
        </div>
    </header>

    <!-- Main Content Container -->
    <main class="max-w-7xl mx-auto px-4 md:px-8 py-6 w-full flex-grow">
        
        <!-- Header Banner -->
        <div class="panel rounded-lg p-6 mb-6">
            <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                    <h1 class="text-xl md:text-2xl font-bold tracking-tight text-white">
                        Container Diagnostic & Diagnostic Suite
                    </h1>
                    <p class="text-slate-400 text-sm mt-1 max-w-3xl">
                        Instanz-Überwachung und HTTP-Endpoint-Validierung für Elastic Container Services (ECS) und Load Balancer Health-Checks.
                    </p>
                </div>
                <div class="flex gap-2">
                    <button onclick="switchTab('diagnostics')" class="px-3.5 py-2 bg-telekom-500 hover:bg-telekom-600 text-white text-xs font-semibold rounded transition flex items-center gap-1.5 shadow-sm">
                        <span>Diagnose starten</span>
                    </button>
                    <a href="/health" target="_blank" class="px-3.5 py-2 bg-[#181c28] hover:bg-[#202636] text-slate-200 text-xs font-medium rounded border border-[#272d40] transition flex items-center gap-1.5">
                        <span>/health Endpoint</span>
                    </a>
                </div>
            </div>
        </div>

        <!-- Metric Stat Cards -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            
            <div class="panel p-4 rounded-lg">
                <div class="text-[11px] uppercase tracking-wider text-slate-400 font-medium mb-1">Serverzeit</div>
                <div id="live-clock" class="text-base font-semibold text-white font-mono">__NOW__</div>
                <div class="text-[11px] text-slate-500 mt-1">UTC Container Timestamp</div>
            </div>

            <div class="panel p-4 rounded-lg">
                <div class="text-[11px] uppercase tracking-wider text-slate-400 font-medium mb-1">Hostname / Instance ID</div>
                <div class="text-base font-semibold text-amber-400 font-mono truncate" title="__HOSTNAME__">__HOSTNAME__</div>
                <div class="text-[11px] text-slate-500 mt-1">Docker Container ID</div>
            </div>

            <div class="panel p-4 rounded-lg">
                <div class="text-[11px] uppercase tracking-wider text-slate-400 font-medium mb-1">Client IP Address</div>
                <div class="text-base font-semibold text-cyan-400 font-mono">__CLIENT_IP__</div>
                <div class="text-[11px] text-slate-500 mt-1">Inbound Request Origin</div>
            </div>

            <div class="panel p-4 rounded-lg">
                <div class="text-[11px] uppercase tracking-wider text-slate-400 font-medium mb-1">Laufzeit</div>
                <div id="uptime-counter" class="text-base font-semibold text-emerald-400 font-mono">__UPTIME__s</div>
                <div class="text-[11px] text-slate-500 mt-1">Active Process Time</div>
            </div>

        </div>

        <!-- Navigation Tabs -->
        <div class="border-b border-[#1e2333] mb-6 flex space-x-6">
            <button onclick="switchTab('overview')" id="tab-btn-overview" class="nav-link active pb-2.5 text-xs text-slate-400 hover:text-white transition">
                Systemübersicht
            </button>
            <button onclick="switchTab('diagnostics')" id="tab-btn-diagnostics" class="nav-link pb-2.5 text-xs text-slate-400 hover:text-white transition">
                Diagnose & Stresstests
            </button>
            <button onclick="switchTab('api')" id="tab-btn-api" class="nav-link pb-2.5 text-xs text-slate-400 hover:text-white transition">
                API Spezifikation
            </button>
        </div>

        <!-- Tab 1: System Overview -->
        <div id="tab-overview" class="tab-content space-y-6">
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <!-- System Specs -->
                <div class="panel rounded-lg p-5 lg:col-span-2">
                    <h3 class="text-sm font-semibold text-white mb-4 flex items-center justify-between border-b border-[#1e2333] pb-3">
                        <span>Laufzeit- Parameter</span>
                        <span class="text-xs font-mono text-slate-400 font-normal">Environment: Production</span>
                    </h3>
                    <div class="grid grid-cols-2 sm:grid-cols-3 gap-3">
                        <div class="bg-[#0e1017] border border-[#1e2333] p-3 rounded">
                            <span class="text-[11px] text-slate-400 block font-medium">Python Version</span>
                            <span class="text-xs font-semibold text-slate-200 font-mono mt-0.5 block">__PYTHON_VERSION__</span>
                        </div>
                        <div class="bg-[#0e1017] border border-[#1e2333] p-3 rounded">
                            <span class="text-[11px] text-slate-400 block font-medium">Betriebssystem</span>
                            <span class="text-xs font-semibold text-slate-200 font-mono mt-0.5 block">__SYSTEM_OS__</span>
                        </div>
                        <div class="bg-[#0e1017] border border-[#1e2333] p-3 rounded">
                            <span class="text-[11px] text-slate-400 block font-medium">CPU Cores</span>
                            <span class="text-xs font-semibold text-slate-200 font-mono mt-0.5 block">__CPU_COUNT__ vCPU</span>
                        </div>
                        <div class="bg-[#0e1017] border border-[#1e2333] p-3 rounded">
                            <span class="text-[11px] text-slate-400 block font-medium">HTTP Port</span>
                            <span class="text-xs font-semibold text-slate-200 font-mono mt-0.5 block">8080</span>
                        </div>
                        <div class="bg-[#0e1017] border border-[#1e2333] p-3 rounded">
                            <span class="text-[11px] text-slate-400 block font-medium">CI/CD Engine</span>
                            <span class="text-xs font-semibold text-emerald-400 font-mono mt-0.5 block">GitHub Actions</span>
                        </div>
                        <div class="bg-[#0e1017] border border-[#1e2333] p-3 rounded">
                            <span class="text-[11px] text-slate-400 block font-medium">Cloud Target</span>
                            <span class="text-xs font-semibold text-telekom-500 font-mono mt-0.5 block">T Cloud Public</span>
                        </div>
                    </div>
                </div>

                <!-- Component Stack -->
                <div class="panel rounded-lg p-5">
                    <h3 class="text-sm font-semibold text-white mb-4 border-b border-[#1e2333] pb-3">Konfigurierte Services</h3>
                    <ul class="space-y-2 text-xs">
                        <li class="flex items-center justify-between p-2 rounded bg-[#0e1017] border border-[#1e2333]">
                            <span class="text-slate-300">Container Platform</span>
                            <span class="font-mono text-slate-400">ECS Docker</span>
                        </li>
                        <li class="flex items-center justify-between p-2 rounded bg-[#0e1017] border border-[#1e2333]">
                            <span class="text-slate-300">Base Image</span>
                            <span class="font-mono text-slate-400">Python 3.9 Slim</span>
                        </li>
                        <li class="flex items-center justify-between p-2 rounded bg-[#0e1017] border border-[#1e2333]">
                            <span class="text-slate-300">Target Group Health Check</span>
                            <span class="font-mono text-emerald-400">Active (/health)</span>
                        </li>
                        <li class="flex items-center justify-between p-2 rounded bg-[#0e1017] border border-[#1e2333]">
                            <span class="text-slate-300">Reverse Proxy</span>
                            <span class="font-mono text-slate-400">ALB Enabled</span>
                        </li>
                    </ul>
                </div>
            </div>
        </div>

        <!-- Tab 2: Diagnostics -->
        <div id="tab-diagnostics" class="tab-content hidden space-y-6">
            <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
                <!-- Endpoint Action Controls -->
                <div class="lg:col-span-5 space-y-2">
                    <div class="text-[11px] font-bold uppercase tracking-wider text-slate-400 mb-2">Testfunktionen</div>
                    
                    <button onclick="runTest('/api/health')" class="w-full text-left p-3.5 rounded panel hover:border-slate-600 transition flex items-center justify-between group">
                        <div>
                            <div class="text-xs font-semibold text-white group-hover:text-telekom-500 transition">Container Health Check</div>
                            <div class="text-[11px] text-slate-400">Statusabfrage für ALB Target Group</div>
                        </div>
                        <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-[#181c28] text-slate-300 border border-[#272d40]">GET /health</span>
                    </button>

                    <button onclick="runTest('/api/load')" class="w-full text-left p-3.5 rounded panel hover:border-slate-600 transition flex items-center justify-between group">
                        <div>
                            <div class="text-xs font-semibold text-white group-hover:text-amber-400 transition">CPU Stresstest</div>
                            <div class="text-[11px] text-slate-400">3-Sekunden Auslastungssimulation</div>
                        </div>
                        <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-[#181c28] text-slate-300 border border-[#272d40]">GET /api/load</span>
                    </button>

                    <button onclick="runTest('/api/error')" class="w-full text-left p-3.5 rounded panel hover:border-slate-600 transition flex items-center justify-between group">
                        <div>
                            <div class="text-xs font-semibold text-white group-hover:text-rose-400 transition">HTTP 500 Simulation</div>
                            <div class="text-[11px] text-slate-400">Prüfung des Failover-Verhaltens</div>
                        </div>
                        <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-[#181c28] text-slate-300 border border-[#272d40]">GET /api/error</span>
                    </button>

                    <button onclick="runTest('/api/env')" class="w-full text-left p-3.5 rounded panel hover:border-slate-600 transition flex items-center justify-between group">
                        <div>
                            <div class="text-xs font-semibold text-white group-hover:text-cyan-400 transition">Environment Variablen</div>
                            <div class="text-[11px] text-slate-400">Maskierte Laufzeit-Variablen</div>
                        </div>
                        <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-[#181c28] text-slate-300 border border-[#272d40]">GET /api/env</span>
                    </button>

                    <button onclick="runTest('/api/headers')" class="w-full text-left p-3.5 rounded panel hover:border-slate-600 transition flex items-center justify-between group">
                        <div>
                            <div class="text-xs font-semibold text-white group-hover:text-purple-400 transition">Request Headers</div>
                            <div class="text-[11px] text-slate-400">Inbound HTTP-Header-Analyse</div>
                        </div>
                        <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-[#181c28] text-slate-300 border border-[#272d40]">GET /api/headers</span>
                    </button>

                    <button onclick="runTest('/api/deployment')" class="w-full text-left p-3.5 rounded panel hover:border-slate-600 transition flex items-center justify-between group">
                        <div>
                            <div class="text-xs font-semibold text-white group-hover:text-emerald-400 transition">Deployment Inspector</div>
                            <div class="text-[11px] text-slate-400">GitHub Actions & Commit Metadaten</div>
                        </div>
                        <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-[#181c28] text-slate-300 border border-[#272d40]">GET /api/deployment</span>
                    </button>
                </div>

                <!-- Console Display -->
                <div class="lg:col-span-7 flex flex-col">
                    <div class="flex justify-between items-center mb-2">
                        <span class="text-[11px] font-bold uppercase tracking-wider text-slate-400">Konsole</span>
                        <span id="response-status" class="text-[11px] font-mono font-medium px-2 py-0.5 rounded bg-[#181c28] text-slate-400 border border-[#272d40]">Bereit</span>
                    </div>
                    
                    <div class="panel rounded-lg p-4 flex-grow flex flex-col font-mono text-xs overflow-hidden min-h-[340px]">
                        <div class="flex items-center justify-between pb-3 border-b border-[#1e2333] text-slate-400">
                            <span id="console-endpoint">Wählen Sie einen Endpunkt aus...</span>
                            <span id="console-time" class="text-slate-500">-- ms</span>
                        </div>
                        <pre id="console-output" class="p-3 text-slate-300 overflow-x-auto whitespace-pre-wrap flex-grow font-mono leading-relaxed">// Antwortergebnisse erscheinen hier...</pre>
                    </div>
                </div>
            </div>
        </div>

        <!-- Tab 3: API Reference -->
        <div id="tab-api" class="tab-content hidden space-y-6">
            <div class="panel rounded-lg overflow-hidden">
                <div class="p-4 border-b border-[#1e2333]">
                    <h3 class="text-sm font-semibold text-white">Verfügbare Endpunkte</h3>
                </div>

                <div class="overflow-x-auto">
                    <table class="w-full text-left text-xs text-slate-300">
                        <thead class="bg-[#0e1017] text-[11px] uppercase tracking-wider text-slate-400 border-b border-[#1e2333]">
                            <tr>
                                <th class="p-3">Methode</th>
                                <th class="p-3">Endpoint</th>
                                <th class="p-3">Beschreibung</th>
                                <th class="p-3">Verwendung</th>
                                <th class="p-3 text-right">Aktion</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-[#1e2333] font-mono">
                            <tr class="hover:bg-[#151824]">
                                <td class="p-3"><span class="px-1.5 py-0.5 rounded bg-[#181c28] text-blue-400 border border-[#272d40]">GET</span></td>
                                <td class="p-3 font-semibold text-white">/health</td>
                                <td class="p-3 text-slate-400 font-sans">Health Check Status & Uptime</td>
                                <td class="p-3 text-emerald-400 font-sans">ALB Target Groups</td>
                                <td class="p-3 text-right font-sans"><a href="/health" target="_blank" class="text-telekom-500 hover:underline">Öffnen</a></td>
                            </tr>
                            <tr class="hover:bg-[#151824]">
                                <td class="p-3"><span class="px-1.5 py-0.5 rounded bg-[#181c28] text-blue-400 border border-[#272d40]">GET</span></td>
                                <td class="p-3 font-semibold text-white">/api/metrics</td>
                                <td class="p-3 text-slate-400 font-sans">Container & OS Metriken</td>
                                <td class="p-3 text-cyan-400 font-sans">Monitoring</td>
                                <td class="p-3 text-right font-sans"><a href="/api/metrics" target="_blank" class="text-telekom-500 hover:underline">Öffnen</a></td>
                            </tr>
                            <tr class="hover:bg-[#151824]">
                                <td class="p-3"><span class="px-1.5 py-0.5 rounded bg-[#181c28] text-blue-400 border border-[#272d40]">GET</span></td>
                                <td class="p-3 font-semibold text-white">/api/load</td>
                                <td class="p-3 text-slate-400 font-sans">CPU-Auslastungssimulation (3s)</td>
                                <td class="p-3 text-amber-400 font-sans">Auto-Scaling Test</td>
                                <td class="p-3 text-right font-sans"><a href="/api/load" target="_blank" class="text-telekom-500 hover:underline">Öffnen</a></td>
                            </tr>
                            <tr class="hover:bg-[#151824]">
                                <td class="p-3"><span class="px-1.5 py-0.5 rounded bg-[#181c28] text-blue-400 border border-[#272d40]">GET</span></td>
                                <td class="p-3 font-semibold text-white">/api/error</td>
                                <td class="p-3 text-slate-400 font-sans">Simuliert HTTP 500 Fehler</td>
                                <td class="p-3 text-rose-400 font-sans">Failover Test</td>
                                <td class="p-3 text-right font-sans"><a href="/api/error" target="_blank" class="text-telekom-500 hover:underline">Öffnen</a></td>
                            </tr>
                            <tr class="hover:bg-[#151824]">
                                <td class="p-3"><span class="px-1.5 py-0.5 rounded bg-[#181c28] text-blue-400 border border-[#272d40]">GET</span></td>
                                <td class="p-3 font-semibold text-white">/api/env</td>
                                <td class="p-3 text-slate-400 font-sans">Umgebungsvariablen auslesen</td>
                                <td class="p-3 text-purple-400 font-sans">Parameter Audit</td>
                                <td class="p-3 text-right font-sans"><a href="/api/env" target="_blank" class="text-telekom-500 hover:underline">Öffnen</a></td>
                            </tr>
                            <tr class="hover:bg-[#151824]">
                                <td class="p-3"><span class="px-1.5 py-0.5 rounded bg-[#181c28] text-blue-400 border border-[#272d40]">GET</span></td>
                                <td class="p-3 font-semibold text-white">/api/headers</td>
                                <td class="p-3 text-slate-400 font-sans">Inbound Request Header</td>
                                <td class="p-3 text-indigo-400 font-sans">Proxy Inspection</td>
                                <td class="p-3 text-right font-sans"><a href="/api/headers" target="_blank" class="text-telekom-500 hover:underline">Öffnen</a></td>
                            </tr>
                            <tr class="hover:bg-[#151824]">
                                <td class="p-3"><span class="px-1.5 py-0.5 rounded bg-[#181c28] text-blue-400 border border-[#272d40]">GET</span></td>
                                <td class="p-3 font-semibold text-white">/api/deployment</td>
                                <td class="p-3 text-slate-400 font-sans">CI/CD Deployment Metadaten</td>
                                <td class="p-3 text-emerald-400 font-sans">Pipeline Validation</td>
                                <td class="p-3 text-right font-sans"><a href="/api/deployment" target="_blank" class="text-telekom-500 hover:underline">Öffnen</a></td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

    </main>

    <!-- Footer -->
    <footer class="bg-[#0e1017] border-t border-[#1e2333] py-4 px-4 text-xs text-slate-500">
        <div class="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
            <div>
                <span>T Cloud Public Container Infrastructure</span>
            </div>
            <div class="font-mono text-[11px] text-slate-500">
                Port 8080 &bull; Python 3.9 Runtime
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
            document.querySelectorAll('.nav-link').forEach(el => el.classList.remove('active'));

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
            statusLabel.className = 'text-[11px] font-mono font-medium px-2 py-0.5 rounded bg-amber-950/60 text-amber-300 border border-amber-800/60';

            const start = performance.now();
            try {
                const res = await fetch(endpoint);
                const duration = Math.round(performance.now() - start);
                const data = await res.json();

                timeLabel.innerText = duration + ' ms';
                statusLabel.innerText = res.status + ' ' + res.statusText;

                if (res.ok) {
                    statusLabel.className = 'text-[11px] font-mono font-medium px-2 py-0.5 rounded bg-emerald-950/60 text-emerald-300 border border-emerald-800/60';
                    output.className = 'p-3 text-emerald-400 overflow-x-auto whitespace-pre-wrap flex-grow font-mono leading-relaxed';
                } else {
                    statusLabel.className = 'text-[11px] font-mono font-medium px-2 py-0.5 rounded bg-rose-950/60 text-rose-300 border border-rose-800/60';
                    output.className = 'p-3 text-rose-400 overflow-x-auto whitespace-pre-wrap flex-grow font-mono leading-relaxed';
                }

                output.innerText = JSON.stringify(data, null, 2);
            } catch (err) {
                const duration = Math.round(performance.now() - start);
                timeLabel.innerText = duration + ' ms';
                statusLabel.innerText = 'FETCH ERROR';
                statusLabel.className = 'text-[11px] font-mono font-medium px-2 py-0.5 rounded bg-rose-950/60 text-rose-300 border border-rose-800/60';
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
        elif path == '/api/deployment':
            self.handle_deployment_status()
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
                    "/api/headers",
                    "/api/deployment"
                ]
            }, 404)

    def handle_health(self):
        uptime = int(time.time() - START_TIME)
        data = {
            "status": "UP",
            "service": "t-cloud-ecs-app",
            "hostname": socket.gethostname(),
            "uptime_seconds": uptime,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }
        self.send_json_response(data, 200)

    def handle_metrics(self):
        uptime = int(time.time() - START_TIME)
        data = {
            "service": "t-cloud-ecs-app",
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

    def handle_deployment_status(self):
        uptime = int(time.time() - START_TIME)
        commit_hash = os.environ.get('GIT_COMMIT_SHA', os.environ.get('GITHUB_SHA', '18b8d00 (main)'))
        data = {
            "status": "success",
            "feature": "CD Pipeline Inspector v2.1",
            "pipeline": {
                "provider": "GitHub Actions",
                "trigger": "Push to main branch",
                "workflow": ".github/workflows/deploy.yml",
                "status": "ACTIVE / DEPLOYED"
            },
            "environment": {
                "hostname": socket.gethostname(),
                "os": f"{platform.system()} {platform.release()}",
                "python_version": platform.python_version(),
                "commit": commit_hash,
                "uptime_seconds": uptime
            },
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }
        self.send_json_response(data, 200)

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
    print(" [INFO] T Cloud Public Diagnostic Dashboard v2.0")
    print(f" [INFO] Server gestartet auf Port {port}")
    print(f" [INFO] Health Check Route: http://localhost:{port}/health")
    print("==================================================")
    server = HTTPServer(('0.0.0.0', port), CloudDashboardHandler)
    server.serve_forever()