from app.notes import Notes
from app.search import Search


def make(*items):
    n = Notes()
    for owner, text in items:
        n.create(owner, text)
    return n, Search(n)


def test_search_is_case_insensitive():
    _, s = make(("sam", "Buy MILK"))
    assert [x["text"] for x in s.find("sam", "milk")] == ["Buy MILK"]
    assert [x["text"] for x in s.find("sam", "MiLk")] == ["Buy MILK"]


def test_search_returns_only_matching_notes():
    _, s = make(("sam", "Buy milk"), ("sam", "Call mum"))
    assert [x["text"] for x in s.find("sam", "mum")] == ["Call mum"]
    assert s.find("sam", "zebra") == []


def test_search_never_returns_another_users_notes():
    _, s = make(("sam", "sam milk"), ("kim", "kim milk"))
    assert [x["owner"] for x in s.find("sam", "milk")] == ["sam"]
    assert [x["owner"] for x in s.find("kim", "milk")] == ["kim"]


def test_search_sees_notes_added_after_an_earlier_search():
    n, s = make(("sam", "Buy milk"))
    assert len(s.find("sam", "milk")) == 1
    n.create("sam", "More milk")
    assert sorted(x["text"] for x in s.find("sam", "milk")) == ["Buy milk", "More milk"]


def test_search_unicode():
    _, s = make(("sam", "Café 日本"))
    assert len(s.find("sam", "café")) == 1
    assert len(s.find("sam", "日本")) == 1
