import sqlite3
import json
import os
from typing import Optional
from data.models import Favorite, HistoryItem, Recipe
from config import DB_NAME


def get_db_path() -> str:
    # На Android Flet сохраняет в app data dir
    base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, "..", DB_NAME)


class Database:
    def __init__(self):
        self.path = get_db_path()
        self._init_schema()

    def _conn(self):
        return sqlite3.connect(self.path)

    def _init_schema(self):
        with self._conn() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS favorites (
                    id           INTEGER PRIMARY KEY AUTOINCREMENT,
                    title        TEXT NOT NULL,
                    json_data    TEXT NOT NULL,
                    content_hash TEXT UNIQUE,
                    added_at     TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS history (
                    id         INTEGER PRIMARY KEY AUTOINCREMENT,
                    title      TEXT NOT NULL,
                    json_data  TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS app_state (
                    key   TEXT PRIMARY KEY,
                    value TEXT
                );
            """)

    # ── Favorites ──────────────────────────────────────────────────

    def add_favorite(self, recipe: Recipe) -> bool:
        """Добавить в избранное. False если уже существует."""
        h = recipe.content_hash()
        with self._conn() as db:
            try:
                db.execute(
                    "INSERT INTO favorites (title, json_data, content_hash, added_at) VALUES (?,?,?,datetime('now'))",
                    (recipe.title, json.dumps(recipe.to_dict(), ensure_ascii=False), h),
                )
                return True
            except sqlite3.IntegrityError:
                return False

    def remove_favorite(self, fav_id: int):
        with self._conn() as db:
            db.execute("DELETE FROM favorites WHERE id=?", (fav_id,))

    def get_favorites(self) -> list[Favorite]:
        with self._conn() as db:
            rows = db.execute(
                "SELECT id, title, json_data, content_hash, added_at FROM favorites ORDER BY added_at DESC"
            ).fetchall()
        return [Favorite(*r) for r in rows]

    def is_favorite(self, recipe: Recipe) -> bool:
        with self._conn() as db:
            row = db.execute(
                "SELECT id FROM favorites WHERE content_hash=?", (recipe.content_hash(),)
            ).fetchone()
        return row is not None

    # ── History ────────────────────────────────────────────────────

    def add_history(self, recipe: Recipe):
        with self._conn() as db:
            db.execute(
                "INSERT INTO history (title, json_data, created_at) VALUES (?,?,datetime('now'))",
                (recipe.title, json.dumps(recipe.to_dict(), ensure_ascii=False)),
            )
            # Оставляем только 50 последних
            db.execute(
                "DELETE FROM history WHERE id NOT IN "
                "(SELECT id FROM history ORDER BY created_at DESC LIMIT 50)"
            )

    def get_history(self, limit: int = 20) -> list[HistoryItem]:
        with self._conn() as db:
            rows = db.execute(
                "SELECT id, title, json_data, created_at FROM history ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [HistoryItem(*r) for r in rows]

    # ── App State ──────────────────────────────────────────────────

    def save_state(self, key: str, value: str):
        with self._conn() as db:
            db.execute(
                "INSERT INTO app_state (key, value) VALUES (?,?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (key, value),
            )

    def load_state(self, key: str, default: str = "") -> str:
        with self._conn() as db:
            row = db.execute(
                "SELECT value FROM app_state WHERE key=?", (key,)
            ).fetchone()
        return row[0] if row else default

    def save_last_recipe(self, recipe: Optional[Recipe]):
        val = json.dumps(recipe.to_dict(), ensure_ascii=False) if recipe else ""
        self.save_state("last_recipe", val)

    def load_last_recipe(self) -> Optional[Recipe]:
        val = self.load_state("last_recipe")
        if not val:
            return None
        try:
            return Recipe.from_dict(json.loads(val))
        except Exception:
            return None
