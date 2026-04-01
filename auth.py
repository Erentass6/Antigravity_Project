import hashlib
from typing import Optional
from config import Config
from database import db

class AuthManager:
    def __init__(self):
        self.collection = db.get_collection(Config.USERS_COLLECTION)
        self._current_user = None

    def register(self, username, password):
        if self.collection.find_one({"username": username}):
            return False, "User already exists!"
        
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        self.collection.insert_one({"username": username, "password": hashed_pw})
        return True, "Registration successful!"

    def login(self, username, password):
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        user = self.collection.find_one({"username": username, "password": hashed_pw})
        if user:
            self._current_user = username
            return True, f"Welcome {username}!"
        return False, "Invalid credentials!"

    def current_user(self) -> Optional[str]:
        return self._current_user

auth = AuthManager()