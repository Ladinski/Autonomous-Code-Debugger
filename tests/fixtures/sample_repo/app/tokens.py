def create_access_token(user_id: int) -> str:
    return f"access-token-{user_id}"


def validate_access_token(token: str) -> bool:
    return token.startswith("access-token-")