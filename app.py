from http.server import HTTPServer, BaseHTTPRequestHandler

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        response = """
        <html>
            <body style="font-family: Arial; text-align: center; margin-top: 50px;">
                <h1>Mein erstes Cloud-Projekt!</h1>
                <p>Diese Webanwendung läuft als Docker-Container auf der T Cloud Public.</p>
            </body>
        </html>
        """
        self.wfile.write(response.encode('utf-8'))

if __name__ == '__main__':
    print("Server startet auf Port 8080...")
    server = HTTPServer(('0.0.0.0', 8080), SimpleHTTPRequestHandler)
    server.serve_forever()