from app.notes import Notes
from app.search import Search


def test_find():
    n = Notes()
    n.create("sam", "Buy milk")
    assert Search(n).find("sam", "milk")[0]["text"] == "Buy milk"
