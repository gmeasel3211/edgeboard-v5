from app.security import hash_password, verify_password


def test_password_round_trip() -> None:
    password = "VeryStrong!Pass123"
    encoded = hash_password(password)
    assert verify_password(password, encoded)
    assert not verify_password("Wrong!Pass123", encoded)
