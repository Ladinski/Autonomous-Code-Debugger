from app.quota import can_make_request


def test_request_below_limit_is_allowed():
    assert can_make_request(
        used_requests=9,
        request_limit=10,
    ) is True


def test_request_at_limit_is_rejected():
    assert can_make_request(
        used_requests=10,
        request_limit=10,
    ) is False