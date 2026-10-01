"""Audit tests for app/server.py through its real HTTP entry point (port 8102)."""
import json
import threading
import urllib.error
import urllib.request

import pytest

from app import server as srv
from app.auth import Auth
from app.notes import Notes
from app.search import Search

PORT = 8102
BASE = f"http://127.0.0.1:{PORT}"


@pytest.fixture(scope="module")
def httpd():
    srv.ThreadingHTTPServer.allow_reuse_address = True
    s = srv.ThreadingHTTPServer(("127.0.0.1", PORT), srv.Handler)
    t = threading.Thread(target=s.serve_forever, daemon=True)
    t.start()
    yield s
    s.shutdown()
    s.server_close()


@pytest.fixture(autouse=True)
def fresh_state(httpd, monkeypatch):
    notes = Notes()
    monkeypatch.setattr(srv, "AUTH", Auth())
    monkeypatch.setattr(srv, "NOTES", notes)
    monkeypatch.setattr(srv, "SEARCH", Search(notes))


def call(method, path, body=None, token=None, raw=None):
    data = raw if raw is not None else (json.dumps(body).encode() if body is not None else None)
    req = urllib.request.Request(BASE + path, data=data, method=method)
    if token:
        req.add_header("Authorization", token)
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


def signup(user="sam", pw="Secret123"):
    assert call("POST", "/register", {"username": user, "password": pw})[0] == 201
    code, body = call("POST", "/login", {"username": user, "password": pw})
    assert code == 200
    return body["token"]


def test_main_journey():
    tok = signup()
    code, note = call("POST", "/notes", {"text": "Buy milk"}, tok)
    assert code == 201 and note["text"] == "Buy milk"
    code, notes = call("GET", "/notes", token=tok)
    assert code == 200 and [n["text"] for n in notes] == ["Buy milk"]


def test_routes_need_login():
    assert call("POST", "/notes", {"text": "x"})[0] == 401
    assert call("GET", "/notes")[0] == 401
    assert call("GET", "/search?q=x")[0] == 401
    assert call("GET", "/notes", token="forged")[0] == 401


def test_bad_login_is_401():
    signup()
    assert call("POST", "/login", {"username": "sam", "password": "nope"})[0] == 401
    assert call("POST", "/login", {"username": "ghost", "password": "nope"})[0] == 401


def test_password_case_sensitive_over_api():
    signup()
    assert call("POST", "/login", {"username": "sam", "password": "SECRET123"})[0] == 401


def test_duplicate_register_is_400():
    signup()
    code, body = call("POST", "/register", {"username": "sam", "password": "x"})
    assert code == 400 and "taken" in body["error"]


def test_missing_fields_on_register_is_400():
    assert call("POST", "/register", {"username": "sam"})[0] == 400


def test_login_missing_password_is_client_error_not_500():
    signup()
    code, _ = call("POST", "/login", {"username": "sam"})
    assert code in (400, 401)


def test_invalid_json_is_400():
    assert call("POST", "/register", raw=b"{not json")[0] == 400


@pytest.mark.parametrize("raw", [b"[1,2]", b"\"text\"", b"5"])
def test_non_object_json_is_400(raw):
    assert call("POST", "/register", raw=raw)[0] == 400


def test_errors_do_not_leak_tracebacks():
    code, body = call("POST", "/login", raw=b"[]")
    assert "Traceback" not in json.dumps(body)
    assert "/app/" not in json.dumps(body)


def test_users_cannot_see_each_others_notes():
    a = signup("alice", "pw-a")
    b = signup("bob", "pw-b")
    call("POST", "/notes", {"text": "alice secret"}, a)
    assert call("GET", "/notes", token=b)[1] == []
    assert call("GET", "/search?q=secret", token=b)[1] == []


def test_unknown_routes_404():
    tok = signup()
    assert call("POST", "/nope", {}, tok)[0] == 404
    assert call("GET", "/nope", token=tok)[0] == 404


def test_concurrent_note_creation_gives_unique_ids():
    # README: "Each note has a unique id."
    from concurrent.futures import ThreadPoolExecutor
    tok = signup()
    with ThreadPoolExecutor(10) as ex:
        results = list(ex.map(lambda i: call("POST", "/notes", {"text": f"n{i}"}, tok), range(20)))
    ids = [body["id"] for code, body in results if code == 201]
    assert len(ids) == 20
    assert len(set(ids)) == 20
    assert len(call("GET", "/notes", token=tok)[1]) == 20


def test_get_errors_still_return_a_response():
    # A bad stored value must not make GET drop the connection with no reply.
    tok = signup()
    call("POST", "/notes", {"text": 123}, tok)
    code, _ = call("GET", "/search?q=a", token=tok)
    assert code in (200, 400, 500)
