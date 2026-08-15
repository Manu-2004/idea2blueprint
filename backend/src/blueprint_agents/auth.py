import secrets
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import bcrypt

from blueprint_agents.db import Database

SESSION_TTL = timedelta(days=30)


@dataclass
class User:
    id: str
    name: str
    email: str


class EmailAlreadyRegistered(Exception):
    pass


class AuthStore:
    def __init__(self, db: Database):
        self._db = db

    def create_user(self, name: str, email: str, password: str) -> User:
        email = email.strip().lower()
        password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        user_id = uuid.uuid4().hex
        created_at = datetime.now(timezone.utc).isoformat()
        with self._db.lock:
            try:
                with self._db.conn:
                    self._db.conn.execute(
                        "INSERT INTO users (id, name, email, password_hash, created_at) "
                        "VALUES (?, ?, ?, ?, ?)",
                        (user_id, name, email, password_hash, created_at),
                    )
            except sqlite3.IntegrityError as exc:
                raise EmailAlreadyRegistered(email) from exc
        return User(id=user_id, name=name, email=email)

    def authenticate(self, email: str, password: str) -> User | None:
        email = email.strip().lower()
        with self._db.lock:
            row = self._db.conn.execute(
                "SELECT id, name, email, password_hash FROM users WHERE email = ?", (email,)
            ).fetchone()
        if row is None:
            return None
        if not bcrypt.checkpw(password.encode("utf-8"), row["password_hash"].encode("utf-8")):
            return None
        return User(id=row["id"], name=row["name"], email=row["email"])

    def create_session(self, user_id: str) -> str:
        token = secrets.token_urlsafe(32)
        now = datetime.now(timezone.utc)
        expires_at = now + SESSION_TTL
        with self._db.lock, self._db.conn:
            self._db.conn.execute(
                "INSERT INTO sessions (token, user_id, created_at, expires_at) VALUES (?, ?, ?, ?)",
                (token, user_id, now.isoformat(), expires_at.isoformat()),
            )
        return token

    def get_user_by_token(self, token: str) -> User | None:
        with self._db.lock:
            row = self._db.conn.execute(
                """
                SELECT users.id, users.name, users.email, sessions.expires_at
                FROM sessions JOIN users ON users.id = sessions.user_id
                WHERE sessions.token = ?
                """,
                (token,),
            ).fetchone()
        if row is None:
            return None
        if datetime.fromisoformat(row["expires_at"]) < datetime.now(timezone.utc):
            return None
        return User(id=row["id"], name=row["name"], email=row["email"])

    def delete_session(self, token: str) -> None:
        with self._db.lock, self._db.conn:
            self._db.conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
