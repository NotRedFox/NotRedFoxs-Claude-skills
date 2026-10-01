from app.auth import Auth


def test_register_and_login():
    a = Auth()
    a.register("sam", "Secret123")
    assert a.login("sam", "Secret123")


def test_unknown_user():
    assert Auth().login("nobody", "x") is None
