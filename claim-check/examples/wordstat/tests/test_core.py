import pytest
from wordstat import count_words, top_words


def test_counts():
    assert count_words("a b a")["a"] == 2


def test_case_folded():
    assert count_words("A a")["a"] == 2


def test_case_kept():
    assert count_words("A a", ignore_case=False)["A"] == 0


def test_top():
    assert top_words("x y x z x y", 2) == [("x", 3), ("y", 2)]


def test_stopwords():
    assert top_words("the cat the", 1, stopwords=["the"]) == [("cat", 1)]


def test_type():
    with pytest.raises(TypeError):
        count_words(None)


def test_empty():
    assert top_words("") == []
