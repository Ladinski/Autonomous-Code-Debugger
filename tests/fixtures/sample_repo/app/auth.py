from app.tokens import (
    create_access_token,
    validate_refresh_token,
)


def login(user_id: int) -> str:
    return create_access_token(user_id)


def refresh_access_token(
    refresh_token: str,
    user_id: int,
) -> str:
    if not validate_refresh_token(refresh_token):
        raise PermissionError("Invalid refresh token.")

    return create_access_token(user_id)