import json
import google.generativeai as genai
from config import GEMINI_API_KEY, GEMINI_MODEL, SYSTEM_PROMPT, MAX_HISTORY_PAIRS
from data.models import Recipe
from typing import Optional


genai.configure(api_key=GEMINI_API_KEY)


class GeminiClient:
    """
    Обёртка над Gemini API.
    - Всегда JSON mode (response_mime_type)
    - Автоматический trim контекста:
        system + первый user + последний model JSON + текущий запрос
    """

    def __init__(self):
        self.model = genai.GenerativeModel(
            model_name=GEMINI_MODEL,
            system_instruction=SYSTEM_PROMPT,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                temperature=0.7,
                max_output_tokens=2048,
            ),
        )
        self._full_history: list[dict] = []  # {"role": "user"|"model", "parts": [str]}

    def _trim_history(self) -> list[dict]:
        """
        Контекст: system prompt (в модели) + первый user + последний model + текущий.
        Оставляем первую пару + последнюю пару, всё лишнее выбрасываем.
        """
        if len(self._full_history) <= MAX_HISTORY_PAIRS * 2:
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
        # Если последняя модель — не вторая, добавляем её
        if last_model and last_model is not first_model:
            trimmed.append(last_model)
        return trimmed

    async def send_message(self, user_text: str) -> tuple[str, Optional[Recipe]]:
        """
        Отправляет сообщение, возвращает (message_text, Recipe|None).
        """
        history_to_send = self._trim_history()

        chat = self.model.start_chat(
            history=[
                {"role": m["role"], "parts": m["parts"]}
                for m in history_to_send
            ]
        )
        response = await chat.send_message_async(user_text)
        raw = response.text.strip()

        # Сохраняем в полную историю
        self._full_history.append({"role": "user",  "parts": [user_text]})
        self._full_history.append({"role": "model", "parts": [raw]})

        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            # Fallback — попытка извлечь JSON из текста
            import re
            m = re.search(r'\{.*\}', raw, re.DOTALL)
            if m:
                data = json.loads(m.group())
            else:
                return ("Ошибка ответа от API", None)

        message = data.get("message", "")
        recipe_dict = data.get("recipe")
        recipe = Recipe.from_dict(recipe_dict) if recipe_dict else None
        return (message, recipe)

    def reset_context(self):
        """Новый рецепт — сбрасываем историю."""
        self._full_history.clear()

    def inject_recipe_context(self, recipe: Recipe):
        """
        Восстанавливаем контекст из БД (last_recipe).
        Вставляем рецепт как последний ответ модели.
        """
        recipe_json = json.dumps(
            {"message": "Вот твой рецепт", "recipe": recipe.to_dict()},
            ensure_ascii=False,
        )
        if not self._full_history:
            self._full_history.append(
                {"role": "user",  "parts": ["Продолжи работу с рецептом"]}
            )
        self._full_history.append(
            {"role": "model", "parts": [recipe_json]}
        )
