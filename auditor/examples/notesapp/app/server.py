import json
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from .auth import Auth
from .notes import Notes
from .search import Search

AUTH = Auth()
NOTES = Notes()
SEARCH = Search(NOTES)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def _send(self, code, body):
        data = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _user(self):
        return AUTH.user_for(self.headers.get("Authorization", ""))

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length) or b"{}")
            path = urlparse(self.path).path
            if path == "/register":
                AUTH.register(body.get("username"), body.get("password"))
                return self._send(201, {"ok": True})
            if path == "/login":
                token = AUTH.login(body.get("username"), body.get("password"))
                if not token:
                    return self._send(401, {"error": "bad login"})
                return self._send(200, {"token": token})
            if path == "/notes":
                user = self._user()
                if not user:
                    return self._send(401, {"error": "login required"})
                note = NOTES.create(user, body.get("text", ""))
                for key in [k for k in SEARCH.cache if k[0] == user]:
                    del SEARCH.cache[key]
                return self._send(201, note)
            return self._send(404, {"error": "not found"})
        except ValueError as e:
            return self._send(400, {"error": str(e)})
        except Exception:
            return self._send(500, {"error": "internal error"})

    def do_GET(self):
        url = urlparse(self.path)
        user = self._user()
        if not user:
            return self._send(401, {"error": "login required"})
        if url.path == "/notes":
            return self._send(200, NOTES.list_for(user))
        if url.path == "/search":
            q = parse_qs(url.query).get("q", [""])[0]
            return self._send(200, SEARCH.find(user, q))
        return self._send(404, {"error": "not found"})


def main(port=8000):
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()


if __name__ == "__main__":
    import sys
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 8000)
