from http.server import HTTPServer, BaseHTTPRequestHandler


class HelloWorldHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        page = """\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hello World App</title>
</head>
<body>
    <h1>Hello World</h1>
</body>
</html>
"""
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(page.encode("utf-8"))


if __name__ == "__main__":
    server = HTTPServer(("localhost", 8000), HelloWorldHandler)
    print("Serving Hello Woererwrwerwerwerld at http://localhost:8000")
    print("Press Ctrl+C to stop")
    server.serve_forever()