def can_make_request(
    used_requests: int,
    request_limit: int,
) -> bool:
    return used_requests <= request_limit