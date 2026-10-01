# Audit: notes and search

Date 2026-10-01. Estimated 1 hour, took 16 minutes (15:25 to 15:41 UTC).

## Summary
- Verdict: Not ready.
- Findings: 4 high, 4 medium, 4 low.
- Tests: 1 existing for this branch (1 pass, 0 fail, 0 flaky over 3 runs), 18 added (6 fail on the current code because of findings A1 to A3 and A5 to A6, 12 pass). Mutations caught: before 24 of 45, after 37 of 45 (mutmut on notes.py and search.py: 24 of 37 before, 29 of 37 after counting 1 timeout; hand mutations on the routes in server.py: 0 of 8 before, 8 of 8 after).

## Permissions used
| # | Asked | Answer | Used |
|---|---|---|---|
| 1 | Start a local server on 127.0.0.1:8101 | Yes | Used for simulated users, load and long run. Route tests also bind 8101. |
| 2 | Load and long tests, up to 10 minutes in total | Yes | About 6 minutes used (load ramp 48 s, long run 4 min 15 s, parallel journeys about 10 s). |
| 3 | pip install mutmut and coverage into a venv in /tmp | Yes | Venv at /tmp/aud-venv. |

Nothing else was asked. No fallbacks were needed. Mutation runs and the fix check were done in copies under /tmp so the project code was not touched.

## Map

Files read in full: app/notes.py, app/search.py, app/server.py, app/auth.py, tests/test_search.py, tests/test_auth.py, README.md.

Entry points
- `Notes.create(owner, text, tags=[])`, `Notes.list_for(owner)` in app/notes.py.
- `Search.find(owner, query)` in app/search.py.
- HTTP routes in app/server.py: `POST /notes`, `GET /notes`, `GET /search?q=`.

Depends on: app/auth.py (`AUTH.user_for(token)` turns the Authorization header into a username). Nothing else depends on this branch; server.py holds one module-level `NOTES` and one `SEARCH` for the whole process.

Data flow for a search
1. Client sends `GET /search?q=milk` with `Authorization: <token>`.
2. `Handler.do_GET` calls `AUTH.user_for` and returns 401 if there is no user.
3. The query string is parsed with `parse_qs`; a missing `q` becomes `""`.
4. `Search.find(user, q)` looks up `(user, q)` in its cache. On a miss it calls `Notes.list_for(user)`, which scans every note of every user, and keeps notes whose lowercased text contains the lowercased query.
5. The list is stored in the cache and returned as JSON.

Data flow for creating a note
1. `POST /notes` reads `Content-Length` bytes and parses JSON.
2. Login is checked, then `Notes.create(user, body.get("text", ""))`.
3. `create` reads `next_id`, sleeps 1 ms, writes `next_id + 1`, appends `"note"` to the `tags` list and stores the note in `self.notes[id]`.

Where state lives: all in process memory. `Notes.notes` (dict of id to note), `Notes.next_id`, the default `tags` list on the `create` function object, and `Search.cache` (dict of `(owner, query)` to result list). Nothing is persisted; a restart loses everything.

## Findings

### A1. Concurrent note creation loses notes. High
- Where: app/notes.py, `Notes.create`.
- What happens: `nid = self.next_id`, then `time.sleep(0.001)`, then `self.next_id = nid + 1`, with no lock, under `ThreadingHTTPServer`. Two requests get the same id and the second overwrites the first in `self.notes`. The first user got a 201 with an id that now belongs to someone else's note, and their note is gone. README says "Each note has a unique id."
- How it was found:
  - In process, 20 threads each creating one note: `20 concurrent creates -> stored notes: 4 next_id: 5`.
  - Over HTTP, parallel users each creating 3 notes then listing and searching:
    ```
    N=10 users: ids returned=30 unique=16, users with errors=7
    N=50 users: ids returned=150 unique=88, users with errors=37
    N=100 users: ids returned=279 unique=145, users with errors=87
    N=200 users: ids returned=551 unique=294, users with errors=173
    ```
    Errors were missing notes (`list mismatch, 0` and `search 200, 0`). No user saw another user's note text, because the overwritten id is re-owned by the writer.
  - Test `test_ids_stay_unique_when_notes_are_created_at_the_same_time` fails on the current code.
- Suggested fix: take a `threading.Lock` around reading and incrementing `next_id` and storing the note (or use `itertools.count()`), and remove the sleep.

### A2. Every note shares one tags list that grows forever. High
- Where: app/notes.py, `create(self, owner, text, tags=[])` and `tags.append("note")`.
- What happens: the default list is created once for the whole process. Every note, for every user and every `Notes()` instance, holds the same list, and each create appends another `"note"`. After two creates: `tags a: ['note', 'note'] tags b: ['note', 'note'] same obj: True`. A note created after 3,000 others has 3,001 tags. Any JSON response that lists k notes repeats that list k times, so `GET /notes` grows with the square of the note count:
  ```
  100 notes, fresh process -> GET /notes body 0.09 MB
  1000 notes, fresh process -> GET /notes body 8.05 MB
  3000 notes, fresh process -> GET /notes body 72.16 MB
  ```
  It also leaks between `Notes()` instances in one process (`Notes() in same process starts with tags len 3001`), which makes tests depend on order.
- How it was found: in-process probe, the long run below (throughput fell from 604 to about 30 requests per second and RSS rose from 19 MB to 480 MB in 4 minutes, with 10 users and only 1 in 10 journeys calling `GET /notes`), and tests `test_creating_a_note_does_not_change_an_earlier_note` and `test_a_new_store_starts_clean`, which fail now.
- Suggested fix: `tags=None`, then `tags = list(tags or []) + ["note"]`.

### A3. Search returns stale results after a new note is added. High
- Where: app/search.py, `Search.find` and `self.cache`.
- What happens: the cache key is `(owner, query)` and nothing clears it when `Notes.create` runs. Over HTTP: search "milk" returns `Buy milk`; then `POST /notes {"text": "Milk again"}` returns 201; the same search still returns only `Buy milk`. The user cannot find a note they wrote a moment ago until the server restarts.
- How it was found: simulated normal user journey and test `test_search_sees_notes_added_after_an_earlier_search`, which fails now.
- Suggested fix: drop the cache (an uncached search over 10,000 notes took 0.41 ms), or clear a user's entries in `create`, or key the cache on a version number that `create` bumps.

### A4. Search cache grows without limit. High
- Where: app/search.py, `self.cache`.
- What happens: each distinct `(owner, query)` pair is stored forever, with its result list. With tracemalloc, 2,000 new queries per step:
  ```
  notes=2000  cache_keys=2000  traced=1.03MB
  notes=4000  cache_keys=4000  traced=2.08MB
  notes=6000  cache_keys=6000  traced=3.28MB
  notes=8000  cache_keys=8000  traced=4.17MB
  notes=10000 cache_keys=10000 traced=5.07MB
  ```
  Top allocations after the run: notes.py:14 1794 KiB, search.py:10 834 KiB, search.py:7 546 KiB. The search.py lines are cache entries. One client can grow server memory by sending many different `q` values.
- How it was found: tracemalloc script and the long run (every search used a new random query).
- Suggested fix: same as A3. If a cache is kept, bound it (for example an LRU of a few thousand entries).

### A5. A note whose text is not a string breaks that user's search for good. Medium
- Where: app/server.py `do_POST` passes `body.get("text", "")` unchecked; app/search.py calls `n["text"].lower()`.
- What happens: `POST /notes {"text": 123}` returns 201. After that, every `GET /search` for that user ends with `RemoteDisconnected: Remote end closed connection without response`, because `do_GET` has no exception handler and the AttributeError (`'int' object has no attribute 'lower'`) kills the request. `{"text": null}` does the same. It stays broken until restart. Other users are not affected.
- How it was found: hostile user script; test `test_non_text_note_is_rejected_or_search_still_answers` fails now.
- Suggested fix: reject non-string `text` with 400 in `create` or the route, and wrap `do_GET` in the same error handling as `do_POST`.

### A6. 500 responses send the full traceback to the client. Medium
- Where: app/server.py `do_POST`, `except Exception: return self._send(500, {"error": traceback.format_exc()})`.
- What happens: `POST /notes` with body `[]` returns 500 with the absolute file path of server.py, the line number and the source line `return self._send(201, NOTES.create(user, body.get("text", "")))`. No secrets were in it, but it shows internals to any client.
- How it was found: hostile user script; test `test_server_errors_do_not_leak_a_traceback` fails now.
- Suggested fix: log the traceback on the server and return `{"error": "internal error"}`. Return 400 for a JSON body that is not an object.

### A7. Connections are reset above about 50 concurrent clients. Medium
- Where: app/server.py `main`, `ThreadingHTTPServer` with the default listen backlog of 5.
- What happens: load ramp, 8 s per step, 70 percent searches and 30 percent creates:
  ```
  conc=  1 rps=  647.0 p50=  1.2ms p95=   2.7ms errors=0/5176
  conc=  5 rps= 1296.0 p50=  3.5ms p95=   6.7ms errors=0/10368
  conc= 10 rps=  939.1 p50=  5.7ms p95=  13.6ms errors=0/7513
  conc= 25 rps= 1166.6 p50=  5.4ms p95=  10.7ms errors=0/9333
  conc= 50 rps= 1098.1 p50=  6.2ms p95=  15.4ms errors=17/8785
  conc=100 rps= 1127.1 p50=  7.0ms p95=1021.0ms errors=66/9017
  ```
  200 parallel `POST /register` calls gave 195 x 201 and 5 x `ConnectionResetError`. The break point is between 25 and 50 concurrent clients, at about 1,100 requests per second.
- How it was found: load script against 127.0.0.1:8101.
- Suggested fix: set `request_queue_size` higher on the server class (for example 128).

### A8. A negative Content-Length holds a server thread until the client gives up. Medium
- Where: app/server.py `do_POST`, `self.rfile.read(length)` with `length = int(header)`.
- What happens: `Content-Length: -1` makes `read(-1)` wait for the client to close the connection. The request hung until the client timeout of 10 s. Many such requests tie up threads.
- How it was found: hostile user script (`neg length: (None, 'TimeoutError: timed out')`).
- Suggested fix: reject a negative or very large Content-Length with 400 or 413.

### A9. No size limit on note text. Low
- Where: `POST /notes`.
- What happens: a 5,000,000-character note was accepted with 201 and is kept in memory.
- Suggested fix: cap text length (for example 100 KB) and the request body size.

### A10. `list_for` scans every user's notes. Low
- Where: app/notes.py `list_for`.
- What happens: with 10,000 notes across 100 users, `list_for` and an uncached search each took 0.41 ms. Cost grows with all notes in the system, not the user's own.
- Suggested fix: keep a dict of owner to note ids.

### A11. Search uses `lower()`, not `casefold()`. Low
- Where: app/search.py.
- What happens: a note `STRASSE` is not found by `straße` (0 results). Other unicode (Café, 日本, emoji) worked.
- Suggested fix: use `casefold()` on both sides if this matters to users.

### A12. Existing tests miss most of the branch. Low
- Where: tests/test_search.py has one test that creates one note and searches for it. It does not import server.py.
- What happens: 13 of 37 mutmut mutants in notes.py and search.py survived, and 0 of 8 route mutations were caught (for example removing the login check on `GET /notes` and `GET /search` passed). None of A1 to A6 would have been caught. Rated Low only because the tests added in this audit now cover it.

## Tests

Existing suite for this branch: `tests/test_search.py`, 1 test, passed in 3 of 3 runs, 0.01 s. Coverage with it alone: notes.py 100 percent, search.py 100 percent, server.py not run.

Added (all use pytest, the project's framework). Each passing test was run against 11 targeted hand mutants of notes.py and search.py, or the 8 route mutants, and failed on at least one:

| File | Test | On current code | Seen failing on a broken version |
|---|---|---|---|
| tests/test_notes_audit.py | test_create_returns_note_with_owner_and_text | Pass | Yes, 2 of 11 targeted hand mutants, for example `"owner": "x"` |
| | test_ids_are_unique | Pass | Yes, hand mutant `self.next_id = nid` |
| | test_every_created_note_is_kept | Pass | Yes, 5 of 11 hand mutants, for example dropping `self.notes[nid] = note` |
| | test_ids_stay_unique_when_notes_are_created_at_the_same_time | Fail (A1) | Yes, the current code |
| | test_creating_a_note_does_not_change_an_earlier_note | Fail (A2) | Yes, the current code |
| | test_a_new_store_starts_clean | Fail (A2) | Yes, the current code |
| | test_list_for_returns_only_that_users_notes | Pass | Yes, 6 of 11 hand mutants, for example `!=` for `==` in `list_for` |
| tests/test_search_audit.py | test_search_is_case_insensitive | Pass | Yes, 6 of 11 hand mutants, for example removing `.lower()` |
| | test_search_returns_only_matching_notes | Pass | Yes, 5 of 11 hand mutants, for example removing the `if q in` filter |
| | test_search_never_returns_another_users_notes | Pass | Yes, 7 of 11 hand mutants, for example searching all notes instead of `list_for(owner)` |
| | test_search_sees_notes_added_after_an_earlier_search | Fail (A3) | Yes, the current code |
| | test_search_unicode | Pass | Yes, 5 of 11 hand mutants, for example an ASCII-only query |
| tests/test_search_routes.py | test_notes_and_search_need_login | Pass | Yes, hand mutations removing either login check |
| | test_user_creates_lists_and_searches | Pass | Yes, hand mutations (200 instead of 201, empty text, raw query) |
| | test_users_do_not_see_each_others_notes | Pass | Yes, hand mutation returning all notes from `GET /notes` |
| | test_non_text_note_is_rejected_or_search_still_answers | Fail (A5) | Yes, the current code |
| | test_server_errors_do_not_leak_a_traceback | Fail (A6) | Yes, the current code |
| | test_search_route_returns_only_matching_notes | Pass | Yes, hand mutations that ignore or empty the query |

The 6 failing tests were checked against a fixed copy in /tmp (lock in `create`, `tags=None`, no cache, string check, generic 500 message): all 18 new tests and the old one passed there, so they test the intended behaviour and not a quirk. The project's app code was not changed.

New and old branch tests run 3 times: `6 failed, 13 passed in 0.68s` each time, no flaky results.

Coverage with the new tests: notes.py 100 percent, search.py 100 percent, server.py 89 percent. Not run: bad-login branch (auth), unknown POST and GET paths (404), the `ValueError` 400 branch, and `main`.

Mutation results
- mutmut 3.8.0 on notes.py and search.py, existing test only: 37 mutants, 24 killed, 13 survived.
- Same, with the new passing tests (the 4 that fail on the current code were deselected, since mutmut needs a green baseline): 28 killed, 1 timeout (`sleep(1.001)`), 8 survived. Survivors: `next_id = 2` at start, `next_id = nid - 1`, `nid + 2`, three changes to the appended tag value, two renames of the `tags` key. Ids stay unique under all three id mutants, and the README does not say what tags should hold, so these are left as open questions, not test gaps.
- Hand mutations on the three routes in server.py, 8 in total: 0 caught by the existing test, 6 caught by the first version of the route tests, 8 caught after adding `test_search_route_returns_only_matching_notes`.

## Checks run
| Check | What was done | Result |
|---|---|---|
| Existing suite x3 | pytest tests/test_search.py | 1 passed each run, 0.01 s |
| Coverage | coverage.py 7.16.2 | 100 / 100 percent; server.py routes not run by old tests |
| Mutation | mutmut, plus 8 hand mutations | See Tests |
| Normal user | register, login, create, list, search over HTTP | Works, except stale search (A3) and growing tags (A2) |
| Confused user | double submit, no token, bad token, missing `q`, missing text | Double submit makes 2 notes (ids 3 and 4); 401 for missing or bad token; missing `q` returns all own notes; missing text stores an empty note |
| Hostile user | script tags, SQL-like query, `../` paths, int text, `[]` body, bad JSON, negative Content-Length, 5 MB text, unicode | Script and SQL-like text stored as plain text and not executed; `../` path gives 404; A5, A6, A8, A9 found |
| Many users | 10, 50, 100, 200 parallel journeys | Notes lost at every level (A1); no cross-user text seen |
| Load | concurrency 1 to 100, 8 s each | Errors from 50 concurrent, p95 1 s at 100 (A7) |
| Long run | 4 min, 4 threads, 19,966 requests, sampled every 10 s | 0 errors; RSS 19 MB to 480 MB; throughput fell from 604 to about 30 requests per second (A2, A4); fds 4 to 8, threads 1 to 5, both back to 4 and 1 when idle |
| Memory | tracemalloc in process | Linear growth in notes.py:14 and search.py:7 and :10 (A4) |
| Security | auth on routes, input to shell or files, secrets, error messages | Login checked on all three routes; no shell, file or query use; no secrets in branch; tracebacks leak (A6) |
| Performance | timed create, list, search | create 1.17 ms (of which 1 ms is the sleep), list_for and cold search 0.41 ms at 10,000 notes |

Long-run samples (RSS of the server process):
```
t=    0s req=     0 err=0 rss=19MB fds=8 threads=5
t=   30s req=  9373 err=0 rss=81MB fds=5 threads=2
t=   60s req= 12272 err=0 rss=146MB fds=7 threads=4
t=   90s req= 14339 err=0 rss=234MB fds=6 threads=3
t=  121s req= 15781 err=0 rss=321MB fds=6 threads=3
t=  161s req= 17424 err=0 rss=507MB fds=8 threads=5
t=  201s req= 18804 err=0 rss=480MB fds=6 threads=3
t=  232s req= 19718 err=0 rss=481MB fds=7 threads=4
end req=19966 err=0 rss=480MB
15s idle after: rss=480MB fds=4 threads=1
```
RSS levelled at about 480 MB only because throughput had fallen to about 30 requests per second; the retained data (A2, A4) keeps growing with every request.

## Not checked
- app/auth.py is a separate branch being audited at the same time. In passing: `register` and `login` lowercase the password before hashing, while the README says passwords are case-sensitive. Not tested here.
- No UI exists, so no browser journeys.
- Long run limited to about 4 minutes to stay inside the 10-minute budget for load and long tests.
- Restart and persistence: everything is in memory by design, so a restart loses all notes. Not treated as a finding because the README does not promise persistence.
- The route tests start a server on port 8101 inside pytest. If something else holds that port the tests will error; a free port (port 0) would be better once the parallel audit is over.
