import json
import urllib.request
import urllib.error
from config import GEMINI_API_KEY, GEMINI_MODEL, SYSTEM_PROMPT
from data.models import Recipe
from typing import Optional

GEMINI_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
)


class GeminiClient:
    def __init__(self):
        self._full_history = []

    def _trim_history(self):
        if len(self._full_history) <= 2:
            return list(self._full_history)
        first_user  = self._full_history[0] if self._full_history else None
        first_model = self._full_history[1] if len(self._full_history) > 1 else None
        last_model  = None
        for msg in reversed(self._full_history):
            if msg["role"] == "model":
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
        contents = []
        for msg in history:
            contents.append({
                "role": msg["role"],
                "parts": [{"text": p} for p in msg["parts"]]
            })
        contents.append({
            "role": "user",
            "parts": [{"text": user_text}]
        })

        payload = json.dumps({
            "system_instruction": {
                "parts": [{"text": SYSTEM_PROMPT}]
            },
            "contents": contents,
            "generationConfig": {
                "response_mime_type": "application/json",
                "temperature": 0.7,
                "maxOutputTokens": 2048
            }
        }).encode("utf-8")

        req = urllib.request.Request(
            GEMINI_URL,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode("utf-8"))
        except urllib.error.URLError as e:
            return (f"Ошибка сети: {e}", None)

        raw = result["candidates"][0]["content"]["parts"][0]["text"]

        self._full_history.append({"role": "user",  "parts": [user_text]})
        self._full_history.append({"role": "model", "parts": [raw]})

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
        import json as _json
        recipe_json = _json.dumps(
            {"message": "Вот твой рецепт", "recipe": recipe.to_dict()},
            ensure_ascii=False,
        )
        if not self._full_history:
            self._full_history.append(
                {"role": "user", "parts": ["Продолжи работу с рецептом"]}
            )
        self._full_history.append(
            {"role": "model", "parts": [recipe_json]}
        )
