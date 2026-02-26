import os

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from .settings import ADMIN_PASSWORD, PASSWORD_HASH_FILE


class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id


def load_password_hash():
    """Return the stored password hash.

    Priority:
    1. data/admin_password.hash (written when password is changed via dashboard)
    2. ADMIN_PASSWORD env var — hashed on the fly
    """
    if os.path.isfile(PASSWORD_HASH_FILE):
        with open(PASSWORD_HASH_FILE, 'r', encoding='utf-8') as f:
            stored = f.read().strip()
            if stored:
                return stored
    # Fall back to env-var plaintext, hashed each call (cheap for login frequency)
    return generate_password_hash(ADMIN_PASSWORD)


def verify_password(plaintext):
    """Return True if plaintext matches the stored/configured password."""
    return check_password_hash(load_password_hash(), plaintext)


def register_user_loader(login_manager):
    @login_manager.user_loader
    def load_user(user_id):
        if user_id == 'admin':
            return User(user_id)
        return None
