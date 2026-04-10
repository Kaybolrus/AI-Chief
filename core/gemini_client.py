import json
import urllib.request
import urllib.error
import asyncio
import time
from config import GEMINI_API_KEY, GEMINI_MODEL, SYSTEM_PROMPT, MAX_HISTORY_PAIRS
from data.models import Recipe
from typing import Optional, Tuple

class GeminiClient:
    def __init__(self):
        self._full_history = []
        self.api_key = GEMINI_API_KEY

    def _trim_history(self):
        """Ограничивает историю согласно настройкам MAX_HISTORY_PAIRS."""
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
        if last_model and last_model is not first_model:
            trimmed.append(last_model)
        return trimmed

    async def send_message(self, user_text: str) -> Tuple[str, Optional[Recipe]]:
        # Формируем актуальный URL (v1beta лучше работает с новыми моделями и реже дает 404)
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{GEMINI_MODEL}:generateContent?key={self.api_key}"
        )

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

        payload_data = {
            "system_instruction": {
                "parts": [{"text": SYSTEM_PROMPT}]
            },
            "contents": contents,
            "generationConfig": {
                "response_mime_type": "application/json",
                "temperature": 0.7,
                "maxOutputTokens": 2048
            }
        }
        
        encoded_payload = json.dumps(payload_data).encode("utf-8")

        # Цикл для обработки ошибки 429 (Retry Logic)
        for attempt in range(3):
            req = urllib.request.Request(
                url,
                data=encoded_payload,
                headers={"Content-Type": "application/json"},
                method="POST"
            )

            try:
                # Используем run_in_executor для синхронного urlopen, чтобы не фризить UI
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(None, lambda: urllib.request.urlopen(req, timeout=30))
                
                with response as resp:
                    result = json.loads(resp.read().decode("utf-8"))
                
                # Если дошли сюда — запрос успешен, выходим из цикла попыток
                break

            except urllib.error.HTTPError as e:
                if e.code == 429:
                    # Ошибка 429: Ждем перед следующей попыткой
                    wait_time = (attempt + 1) * 2
                    await asyncio.sleep(wait_time)
                    if attempt < 2: continue
                    return ("Сервер перегружен (429). Попробуйте через минуту.", None)
                return (f"Ошибка API ({e.code}): {e.reason}", None)
            
            except Exception as e:
                if attempt < 2:
                    await asyncio.sleep(1)
                    continue
                return (f"Ошибка сети: {e}", None)

        # Обработка результата
        try:
            raw = result["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError) as e:
            return (f"Ошибка структуры ответа: {e}", None)

        # Сохраняем в историю
        self._full_history.append({"role": "user",  "parts": [user_text]})
        self._full_history.append({"role": "model", "parts": [raw]})

        try:
            data = json.loads(raw)
            message = data.get("message", "")
            recipe_dict = data.get("recipe")
            recipe = Recipe.from_dict(recipe_dict) if recipe_dict else None
            return (message, recipe)
        except json.JSONDecodeError:
            # Если ИИ вернул текст не в формате JSON, возвращаем как сообщение
            return (raw, None)

    def reset_context(self):
        self._full_history.clear()

    def inject_recipe_context(self, recipe: Recipe):
        recipe_json = json.dumps(
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
