"""Audit tests for app/auth.py, written from the README and function names."""
import pytest

from app.auth import Auth


def make():
    a = Auth()
    a.register("sam", "Secret123")
    return a


def test_passwords_are_case_sensitive():
    # README: "Passwords are case-sensitive."
    a = make()
    assert a.login("sam", "secret123") is None
    assert a.login("sam", "SECRET123") is None


def test_wrong_password_rejected():
    assert make().login("sam", "Secret124") is None


def test_right_password_gives_token_that_maps_to_user():
    a = make()
    token = a.login("sam", "Secret123")
    assert token
    assert a.user_for(token) == "sam"


def test_unknown_token_has_no_user():
    a = make()
    assert a.user_for("not-a-token") is None
    assert a.user_for("") is None


def test_each_login_gives_a_new_token():
    a = make()
    assert a.login("sam", "Secret123") != a.login("sam", "Secret123")


def test_duplicate_username_rejected_and_first_password_kept():
    a = make()
    with pytest.raises(ValueError):
        a.register("sam", "Other999")
    assert a.login("sam", "Secret123")
    assert a.login("sam", "Other999") is None


@pytest.mark.parametrize("user,pw", [("", "x"), ("sam", ""), (None, "x"), ("sam", None)])
def test_register_requires_username_and_password(user, pw):
    with pytest.raises(ValueError):
        Auth().register(user, pw)


def test_register_non_string_password_is_a_value_error():
    # Bad input should give a clear error, not an AttributeError.
    with pytest.raises(ValueError):
        Auth().register("sam", 12345)


def test_login_with_missing_password_returns_none():
    assert make().login("sam", None) is None


def test_unicode_password_round_trip():
    a = Auth()
    a.register("zoë", "pässwörd✓")
    assert a.user_for(a.login("zoë", "pässwörd✓")) == "zoë"
    assert a.login("zoë", "PÄSSWÖRD✓") is None
