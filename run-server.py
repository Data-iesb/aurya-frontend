import http.server, functools

http.server.HTTPServer(("", 8080), functools.partial(http.server.SimpleHTTPRequestHandler, directory="static")).serve_forever()
