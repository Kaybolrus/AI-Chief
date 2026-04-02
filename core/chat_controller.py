from typing import Optional, Callable
from core.gemini_client import GeminiClient
from data.database import Database
from data.models import Recipe


class ChatController:
    """
    Управляет диалогом: отправка → Gemini → обновление state → колбэки UI.
    """

    def __init__(self, db: Database, gemini: GeminiClient):
        self.db = db
        self.gemini = gemini
        self.current_recipe: Optional[Recipe] = None
        self._on_recipe: Optional[Callable] = None
        self._on_message: Optional[Callable] = None
        self._on_error: Optional[Callable] = None

        # Восстанавливаем последний рецепт при старте
        last = db.load_last_recipe()
        if last:
            self.current_recipe = last
            self.gemini.inject_recipe_context(last)

    def on_recipe(self, fn: Callable): self._on_recipe = fn
    def on_message(self, fn: Callable): self._on_message = fn
    def on_error(self, fn: Callable): self._on_error = fn

    async def send(self, user_text: str):
        """Главная точка входа — отправить сообщение шефу."""
        try:
            message, recipe = await self.gemini.send_message(user_text)

            if message and self._on_message:
                self._on_message(message)

            if recipe:
                self.current_recipe = recipe
                self.db.save_last_recipe(recipe)
                self.db.add_history(recipe)
                if self._on_recipe:
                    self._on_recipe(recipe)

        except Exception as e:
            if self._on_error:
                self._on_error(str(e))

    def start_new_recipe(self):
        """Сброс контекста для нового рецепта."""
        self.current_recipe = None
        self.gemini.reset_context()
        self.db.save_last_recipe(None)

    def save_current_to_favorites(self) -> bool:
        if not self.current_recipe:
            return False
        return self.db.add_favorite(self.current_recipe)

    def is_current_favorite(self) -> bool:
        if not self.current_recipe:
            return False
        return self.db.is_favorite(self.current_recipe)
