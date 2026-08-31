from app.auth import refresh_access_token
from app.tokens import create_refresh_token


def test_refresh_access_token():
    refresh_token = create_refresh_token(42)

    access_token = refresh_access_token(
        refresh_token,
        42,
    )

    assert access_token == "access-token-42"