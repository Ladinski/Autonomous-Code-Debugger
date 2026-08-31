from app.tokens import create_access_token


def login(user_id: int) -> str:
    return create_access_token(user_id)


def refresh_access_token(user_id: int) -> str:
    return create_access_token(user_id)