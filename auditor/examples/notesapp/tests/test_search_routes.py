import http.client
import json
import threading

import pytest

from app import server

PORT = 8101  # the only port this audit may use


@pytest.fixture(scope="module")
def srv():
    httpd = server.ThreadingHTTPServer(("127.0.0.1", PORT), server.Handler)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    yield
    httpd.shutdown()
    httpd.server_close()


def call(method, path, body=None, token=None, raw=None):
    c = http.client.HTTPConnection("127.0.0.1", PORT, timeout=5)
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = token
    data = raw if raw is not None else (json.dumps(body).encode() if body is not None else None)
    c.request(method, path, body=data, headers=headers)
    r = c.getresponse()
    out = r.status, json.loads(r.read() or b"null")
    c.close()
    return out


def login(name):
    call("POST", "/register", {"username": name, "password": "Pw12345"})
    return call("POST", "/login", {"username": name, "password": "Pw12345"})[1]["token"]


def test_notes_and_search_need_login(srv):
    assert call("GET", "/notes")[0] == 401
    assert call("GET", "/search?q=a")[0] == 401
    assert call("POST", "/notes", {"text": "x"})[0] == 401


def test_user_creates_lists_and_searches(srv):
    t = login("route_ann")
    status, note = call("POST", "/notes", {"text": "Route milk"}, t)
    assert status == 201 and note["text"] == "Route milk"
    assert [n["text"] for n in call("GET", "/notes", token=t)[1]] == ["Route milk"]
    assert [n["text"] for n in call("GET", "/search?q=milk", token=t)[1]] == ["Route milk"]


def test_users_do_not_see_each_others_notes(srv):
    a, b = login("route_a"), login("route_b")
    call("POST", "/notes", {"text": "secret plan"}, a)
    assert call("GET", "/search?q=secret", token=b)[1] == []
    assert call("GET", "/notes", token=b)[1] == []


def test_non_text_note_is_rejected_or_search_still_answers(srv):
    t = login("route_num")
    status, _ = call("POST", "/notes", {"text": 123}, t)
    if status == 201:
        assert call("GET", "/search?q=1", token=t)[0] == 200
    else:
        assert status == 400


def test_server_errors_do_not_leak_a_traceback(srv):
    t = login("route_tb")
    status, body = call("POST", "/notes", raw=b"[]", token=t)
    assert status in (400, 500)
    assert "Traceback" not in json.dumps(body)
    assert ".py" not in json.dumps(body)


def test_search_route_returns_only_matching_notes(srv):
    t = login("route_many")
    for text in ("Buy eggs", "Call mum", "Eggs for cake"):
        call("POST", "/notes", {"text": text}, t)
    found = sorted(n["text"] for n in call("GET", "/search?q=eggs", token=t)[1])
    assert found == ["Buy eggs", "Eggs for cake"]
