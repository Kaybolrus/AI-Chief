from typing import Optional, Callable
from core.gemini_client import GeminiClient
from data.database import Database
from data.models import Recipe


class ChatController:
    def __init__(self, db: Database, gemini: GeminiClient):
        self.db = db
        self.gemini = gemini
        self.current_recipe: Optional[Recipe] = None
        self._on_recipe: Optional[Callable] = None
        self._on_message: Optional[Callable] = None
        self._on_error: Optional[Callable] = None

        try:
            last = db.load_last_recipe()
            if last:
                self.current_recipe = last
                self.gemini.inject_recipe_context(last)
        except Exception:
            pass

    def on_recipe(self, fn: Callable): self._on_recipe = fn
    def on_message(self, fn: Callable): self._on_message = fn
    def on_error(self, fn: Callable): self._on_error = fn

    async def send(self, user_text: str):
        try:
            message, recipe = await self.gemini.send_message(user_text)

            if message and self._on_message:
                self._on_message(message)

            if recipe:
                self.current_recipe = recipe
                try:
                    self.db.save_last_recipe(recipe)
                    self.db.add_history(recipe)
                except Exception:
                    pass
                if self._on_recipe:
                    self._on_recipe(recipe)

        except OSError:
            if self._on_error:
                self._on_error("Нет интернета. Проверь подключение и попробуй снова.")
        except TimeoutError:
            if self._on_error:
                self._on_error("Сервер не отвечает. Попробуй позже.")
        except Exception as e:
            if self._on_error:
                self._on_error(f"Ошибка: {e}")

    def start_new_recipe(self):
        self.current_recipe = None
        self.gemini.reset_context()
        try:
            self.db.save_last_recipe(None)
        except Exception:
            pass

    def save_current_to_favorites(self) -> bool:
        if not self.current_recipe:
            return False
        try:
            return self.db.add_favorite(self.current_recipe)
        except Exception:
            return False

    def is_current_favorite(self) -> bool:
        if not self.current_recipe:
            return False
        try:
            return self.db.is_favorite(self.current_recipe)
        except Exception:
            return False
