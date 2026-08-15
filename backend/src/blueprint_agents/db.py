import sqlite3
import threading


class Database:
    """A single sqlite3 connection guarded by a lock, shared by every store in the process.

    One connection (not one-per-call) so an in-memory database (`:memory:`, used in tests)
    stays a single database rather than a fresh empty one per connection. All cross-thread
    access is serialized through `lock` rather than relying on sqlite's own connection-level
    thread safety, mirroring the lock-around-a-shared-resource pattern `JobStore` already
    used before this became persistent.
    """

    def __init__(self, path: str):
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.lock = threading.Lock()

    def init_schema(self) -> None:
        with self.lock, self.conn:
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    token TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL REFERENCES users(id),
                    created_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL
                )
                """
            )
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS spec_jobs (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL REFERENCES users(id),
                    title TEXT,
                    brief_json TEXT NOT NULL,
                    status TEXT NOT NULL,
                    spec_json TEXT,
                    error_json TEXT,
                    revision_round INTEGER NOT NULL DEFAULT 0,
                    max_revision_rounds INTEGER NOT NULL DEFAULT 0,
                    events_json TEXT NOT NULL DEFAULT '[]',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            self.conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_spec_jobs_user_updated "
                "ON spec_jobs(user_id, updated_at DESC)"
            )
