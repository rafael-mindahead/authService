from pwdlib import PasswordHash

password_hasher = PasswordHash.recommended()

def hash_password(password: str) -> str:
    return password_hasher.hash(password)

def verify_password(
        plain_password: str,
        hashed_password: str
) -> bool:
    return password_hash.verify(
        plain_password,
        hashed_password
    )