import threading

from app.notes import Notes


def test_create_returns_note_with_owner_and_text():
    n = Notes()
    note = n.create("sam", "Buy milk")
    assert note["owner"] == "sam"
    assert note["text"] == "Buy milk"


def test_ids_are_unique():
    n = Notes()
    ids = [n.create("sam", f"note {i}")["id"] for i in range(5)]
    assert len(set(ids)) == 5


def test_every_created_note_is_kept():
    n = Notes()
    for i in range(5):
        n.create("sam", f"note {i}")
    assert sorted(x["text"] for x in n.list_for("sam")) == [f"note {i}" for i in range(5)]


def test_ids_stay_unique_when_notes_are_created_at_the_same_time():
    # The server is threaded, so two users can create notes at once.
    n = Notes()
    threads = [threading.Thread(target=n.create, args=(f"user{i}", f"text {i}")) for i in range(20)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    for i in range(20):
        assert [x["text"] for x in n.list_for(f"user{i}")] == [f"text {i}"]


def test_creating_a_note_does_not_change_an_earlier_note():
    n = Notes()
    first = n.create("sam", "one")
    tags_before = list(first["tags"])
    n.create("kim", "two")
    assert n.list_for("sam")[0]["tags"] == tags_before


def test_a_new_store_starts_clean():
    Notes().create("sam", "one")
    note = Notes().create("kim", "two")
    assert note["id"] == 1
    assert len(note["tags"]) <= 1


def test_list_for_returns_only_that_users_notes():
    n = Notes()
    n.create("sam", "sam note")
    n.create("kim", "kim note")
    assert [x["text"] for x in n.list_for("sam")] == ["sam note"]
    assert [x["text"] for x in n.list_for("kim")] == ["kim note"]
    assert n.list_for("nobody") == []
