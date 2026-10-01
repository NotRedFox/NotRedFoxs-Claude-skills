import hashlib
import secrets


class Auth:
    def __init__(self):
        self.users = {}
        self.tokens = {}

    def register(self, username, password):
        if not username or not password:
            raise ValueError("username and password are required")
        if username in self.users:
            raise ValueError("username taken")
        self.users[username] = hashlib.sha256(password.encode()).hexdigest()

    def login(self, username, password):
        stored = self.users.get(username)
        if stored is None or stored != hashlib.sha256(password.encode()).hexdigest():
            return None
        token = secrets.token_hex(16)
        self.tokens[token] = username
        return token

    def user_for(self, token):
        return self.tokens.get(token)
