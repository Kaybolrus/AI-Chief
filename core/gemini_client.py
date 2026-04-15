import json
import urllib.request
import urllib.error
from config import GROQ_API_KEY, GROQ_MODEL, SYSTEM_PROMPT, MAX_HISTORY_PAIRS
from data.models import Recipe
from typing import Optional

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

class GeminiClient:  # Имя оставляем — чтобы не менять chat_controller.py
    def __init__(self):
        self._full_history = []

    def _trim_history(self):
        if len(self._full_history) <= MAX_HISTORY_PAIRS * 2:
            return list(self._full_history)
        first_user  = self._full_history[0] if self._full_history else None
        first_model = self._full_history[1] if len(self._full_history) > 1 else None
        last_model  = None
        for msg in reversed(self._full_history):
            if msg["role"] == "assistant":
                last_model = msg
                break
        trimmed = []
        if first_user:  trimmed.append(first_user)
        if first_model: trimmed.append(first_model)
        if last_model and last_model is not first_model:
            trimmed.append(last_model)
        return trimmed

    async def send_message(self, user_text: str) -> tuple[str, Optional[Recipe]]:
        history = self._trim_history()
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for msg in history:
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": user_text})

        payload = json.dumps({
            "model": GROQ_MODEL,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2048,
            "response_format": {"type": "json_object"}  # JSON mode как у Gemini
        }).encode("utf-8")

        req = urllib.request.Request(
            GROQ_URL,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {GROQ_API_KEY}"
            },
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode("utf-8"))
        except urllib.error.URLError as e:
            return (f"Ошибка сети: {e}", None)
        except Exception as e:
            return (f"Ошибка: {e}", None)

        try:
            raw = result["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as e:
            return (f"Ошибка ответа API: {e}", None)

        self._full_history.append({"role": "user",      "content": user_text})
        self._full_history.append({"role": "assistant", "content": raw})

        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return ("Ошибка парсинга ответа", None)

        message = data.get("message", "")
        recipe_dict = data.get("recipe")
        recipe = Recipe.from_dict(recipe_dict) if recipe_dict else None
        return (message, recipe)

    def reset_context(self):
        self._full_history.clear()

    def inject_recipe_context(self, recipe: Recipe):
        recipe_json = json.dumps(
            {"message": "Вот твой рецепт", "recipe": recipe.to_dict()},
            ensure_ascii=False,
        )
        if not self._full_history:
            self._full_history.append(
                {"role": "user", "content": "Продолжи работу с рецептом"}
            )
        self._full_history.append(
            {"role": "assistant", "content": recipe_json}
        )
