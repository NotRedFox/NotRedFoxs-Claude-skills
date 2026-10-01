"""Final audit: tests that cross auth, notes, search and the HTTP server (port 8103)."""
import json
import sys
import threading
import urllib.error
import urllib.request

import pytest

from app import server as srv
from app.auth import Auth
from app.notes import Notes
from app.search import Search

PORT = 8103
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


def call(method, path, body=None, token=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method)
    if token:
        req.add_header("Authorization", token)
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


def signup(user, pw="Secret123"):
    assert call("POST", "/register", {"username": user, "password": pw})[0] == 201
    code, body = call("POST", "/login", {"username": user, "password": pw})
    assert code == 200
    return body["token"]


def texts(notes):
    return sorted(n["text"] for n in notes)


def test_search_over_http_sees_a_note_added_after_an_earlier_search():
    # Full journey across auth, notes, search: a search made before a new note
    # must not hide that note afterwards, and must not touch another user's results.
    sam = signup("sam")
    kim = signup("kim")
    call("POST", "/notes", {"text": "Buy milk"}, sam)
    call("POST", "/notes", {"text": "Milk for kim"}, kim)
    assert texts(call("GET", "/search?q=milk", token=sam)[1]) == ["Buy milk"]
    assert texts(call("GET", "/search?q=milk", token=kim)[1]) == ["Milk for kim"]
    assert call("POST", "/notes", {"text": "Milk again"}, sam)[0] == 201
    assert texts(call("GET", "/search?q=milk", token=sam)[1]) == ["Buy milk", "Milk again"]
    assert texts(call("GET", "/search?q=MILK", token=sam)[1]) == ["Buy milk", "Milk again"]
    assert texts(call("GET", "/search?q=milk", token=kim)[1]) == ["Milk for kim"]


def test_note_creation_does_not_fail_while_other_users_search():
    # Finding F1: POST /notes clears the user's search cache by iterating
    # SEARCH.cache while other request threads add to it. The note is stored,
    # then the request fails with 500 and the clear is left half done.
    old = sys.getswitchinterval()
    sys.setswitchinterval(1e-6)
    try:
        sam = signup("sam")
        for i in range(20000):
            srv.SEARCH.cache[("filler", f"q{i}")] = []
        stop = threading.Event()

        def searcher(n):
            k = 0
            while not stop.is_set():
                k += 1
                srv.SEARCH.find("filler", f"s{n}_{k}")

        threads = [threading.Thread(target=searcher, args=(n,)) for n in range(4)]
        for t in threads:
            t.start()
        try:
            codes = [call("POST", "/notes", {"text": f"n{i}"}, sam)[0] for i in range(30)]
        finally:
            stop.set()
            for t in threads:
                t.join()
    finally:
        sys.setswitchinterval(old)
    assert codes.count(201) == 30, codes
    assert len(call("GET", "/notes", token=sam)[1]) == 30


def test_searching_many_different_words_does_not_keep_every_result():
    # Earlier finding notes-search A4, still open: the search cache keeps one
    # entry per distinct query for a user who never posts, without limit.
    sam = signup("sam")
    call("POST", "/notes", {"text": "Buy milk"}, sam)
    for i in range(3000):
        srv.SEARCH.find("sam", f"word{i}")
    assert len(srv.SEARCH.cache) < 3000
