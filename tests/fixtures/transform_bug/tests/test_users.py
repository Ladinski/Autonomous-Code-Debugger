from app.users import normalize_email


def test_email_whitespace_is_removed():
    assert (
        normalize_email("  user@example.com  ")
        == "user@example.com"
    )


def test_email_is_lowercased():
    assert (
        normalize_email("User@Example.COM")
        == "user@example.com"
    )


def test_email_whitespace_and_case_are_normalized():
    assert (
        normalize_email("  User@Example.COM  ")
        == "user@example.com"
    )