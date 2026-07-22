import datetime
import socket
from http.server import HTTPServer, BaseHTTPRequestHandler

class CloudDashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()

        # Dynamische Daten für das Dashboard
        now = datetime.datetime.now().strftime("%d.%m.%Y - %H:%M:%S Uhr")
        hostname = socket.gethostname()
        client_ip = self.client_address[0]

        # HTML mit Tailwind CSS (über CDN eingebunden)
        html_content = f"""
        <!DOCTYPE html>
        <html lang="de">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Telekom Cloud Dashboard</title>
            <script src="https://cdn.tailwindcss.com"></script>
        </head>
        <body class="bg-slate-900 text-slate-100 min-h-screen flex flex-col justify-between font-sans">

            <nav class="bg-slate-800 border-b border-slate-700 px-6 py-4 flex justify-between items-center shadow-lg">
                <div class="flex items-center space-x-3">
                    <span class="text-2xl">☁️</span>
                    <span class="font-bold text-xl tracking-wide text-magenta-500">OTC Cloud Control</span>
                </div>
                <div class="flex items-center space-x-2">
                    <span class="inline-block w-3 h-3 bg-emerald-500 rounded-full animate-ping"></span>
                    <span class="text-sm font-medium text-emerald-400">Live Status: Running</span>
                </div>
            </nav>

            <main class="max-w-4xl mx-auto px-4 py-8 w-full">
                
                <div class="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-2xl p-6 mb-8 shadow-xl">
                    <h1 class="text-3xl font-extrabold mb-2">🚀 Wilkommen auf deinem ECS Cloud-Server!</h1>
                    <p class="text-blue-100 text-sm">Containerisierte Python-Anwendung, gehostet in der Open Telekom Cloud.</p>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                    
                    <div class="bg-slate-800 border border-slate-700 p-5 rounded-xl shadow-md">
                        <span class="text-xs uppercase tracking-wider text-slate-400 font-bold">Server-Uhrzeit</span>
                        <div class="text-lg font-semibold mt-2 text-indigo-400">{now}</div>
                    </div>

                    <div class="bg-slate-800 border border-slate-700 p-5 rounded-xl shadow-md">
                        <span class="text-xs uppercase tracking-wider text-slate-400 font-bold">Container Hostname</span>
                        <div class="text-lg font-semibold mt-2 text-amber-400 font-mono">{hostname}</div>
                    </div>

                    <div class="bg-slate-800 border border-slate-700 p-5 rounded-xl shadow-md">
                        <span class="text-xs uppercase tracking-wider text-slate-400 font-bold">Deine IP-Adresse</span>
                        <div class="text-lg font-semibold mt-2 text-emerald-400 font-mono">{client_ip}</div>
                    </div>

                </div>

                <div class="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 text-center">
                    <h2 class="text-sm font-semibold uppercase text-slate-400 tracking-wider mb-4">Infrastruktur & Stack</h2>
                    <div class="flex flex-wrap justify-center gap-3">
                        <span class="bg-slate-700 text-slate-200 text-xs px-3 py-1.5 rounded-full font-medium border border-slate-600">Open Telekom Cloud (OTC)</span>
                        <span class="bg-blue-900/60 text-blue-300 text-xs px-3 py-1.5 rounded-full font-medium border border-blue-700">Docker Container</span>
                        <span class="bg-yellow-900/60 text-yellow-300 text-xs px-3 py-1.5 rounded-full font-medium border border-yellow-700">Python 3.9</span>
                        <span class="bg-purple-900/60 text-purple-300 text-xs px-3 py-1.5 rounded-full font-medium border border-purple-700">Tailwind CSS</span>
                        <span class="bg-emerald-900/60 text-emerald-300 text-xs px-3 py-1.5 rounded-full font-medium border border-emerald-700">GitHub Actions CI</span>
                    </div>
                </div>

            </main>

            <footer class="bg-slate-800 border-t border-slate-700 text-center py-4 text-xs text-slate-500">
                Created with ❤️ for Cloud & Web Dev | Open Telekom Cloud Project
            </footer>

        </body>
        </html>
        """
        self.wfile.write(html_content.encode('utf-8'))

if __name__ == '__main__':
    print("Dashboard Server startet auf Port 8080...")
    server = HTTPServer(('0.0.0.0', 8080), CloudDashboardHandler)
    server.serve_forever()