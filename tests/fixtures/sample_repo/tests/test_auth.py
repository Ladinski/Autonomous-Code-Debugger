from app.auth import refresh_access_token


def test_refresh_access_token():
    token = refresh_access_token(42)

    assert token == "access-token-42"