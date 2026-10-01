import pytest

from slug import slugify


def test_plain_title():
    assert slugify("Hello World") == "hello-world"


def test_accents_are_kept_as_letters():
    assert slugify("Café au lait") == "cafe-au-lait"


def test_punctuation_runs_become_one_hyphen():
    assert slugify("Wait... what?!") == "wait-what"


def test_non_latin_title_is_not_empty():
    assert slugify("東京") != ""


def test_different_non_latin_titles_do_not_collide():
    assert slugify("東京") != slugify("大阪")


@pytest.mark.xfail(strict=True, reason="German sharp s is dropped. See the log, open question 1.")
def test_sharp_s_becomes_ss():
    assert slugify("Straße") == "strasse"
