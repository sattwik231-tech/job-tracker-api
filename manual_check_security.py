from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)

# Test password hashing
password = "StrongPass123"
hashed_password = hash_password(password)

print("Hash created:", hashed_password.startswith("$argon2"))
print("Correct password:", verify_password(password, hashed_password))
print("Wrong password:", verify_password("WrongPass123", hashed_password))

# Test JWT creation and decoding
token = create_access_token(user_id=1)
payload = decode_access_token(token)

print("Token created:", isinstance(token, str))
print("Token subject:", payload["sub"])
