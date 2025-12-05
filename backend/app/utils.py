# backend/app/utils.py
import hashlib
import secrets


def hash_password(password: str) -> str:
    """Хеширует пароль с солью"""
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.pbkdf2_hmac(
        'sha256', password.encode(), salt.encode(), 100000)
    return f"{salt}${pwd_hash.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    """Проверяет пароль"""
    try:
        salt, pwd_hash = password_hash.split('$')
        new_hash = hashlib.pbkdf2_hmac(
            'sha256', password.encode(), salt.encode(), 100000)
        return new_hash.hex() == pwd_hash
    except:
        return False
