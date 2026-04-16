import json
import urllib.request
import urllib.error
import asyncio
import ssl
import certifi
from config import OPENROUTER_API_KEY, MODELS_PRIORITY, SYSTEM_PROMPT, MAX_HISTORY_PAIRS
from data.models import Recipe
from typing import Optional, Tuple

class GeminiClient:
    def __init__(self):
        # Очистка ключа от лишних символов
        raw_key = str(OPENROUTER_API_KEY).strip()
        self.api_key = raw_key.replace('"', '').replace("'", "").replace("\n", "").replace("\r", "").strip()
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.history = [] # Хранилище контекста
        
        try:
            self.ssl_context = ssl.create_default_context(cafile=certifi.where())
        except Exception:
            self.ssl_context = None

    async def send_message(self, user_text: str) -> Tuple[str, Optional[Recipe]]:
        """Отправляет запрос, пробуя модели по очереди."""
        if not self.api_key or "YOUR_GROQ" in self.api_key:
            return ("Ошибка: API ключ не настроен.", None)

        last_error = ""
        for model_name in MODELS_PRIORITY:
            try:
                return await self._make_request(model_name, user_text)
            except Exception as e:
                last_error = str(e)
                print(f"Ошибка {model_name}: {e}")
                continue
        
        return (f"Все модели недоступны. Ошибка: {last_error}", None)

    async def _make_request(self, model_name: str, user_text: str) -> Tuple[str, Optional[Recipe]]:
        # Ограничение истории согласно конфигу
        history_limit = MAX_HISTORY_PAIRS * 2
        context = self.history[-history_limit:]
        
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend(context)
        messages.append({"role": "user", "content": user_text})

        payload = {
            "model": model_name,
            "messages": messages,
            "response_format": {"type": "json_object"},
            "temperature": 0.7
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://aichef.pro",
            "X-Title": "AIChefPro"
        }

        req = urllib.request.Request(
            self.api_url, 
            data=json.dumps(payload).encode("utf-8"), 
            headers=headers, 
            method="POST"
        )

        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None, 
            lambda: urllib.request.urlopen(req, context=self.ssl_context, timeout=45)
        )
        
        with response as resp:
            data = json.loads(resp.read().decode("utf-8"))
            content = data["choices"][0]["message"]["content"]
            
            try:
                res_data = json.loads(content)
                # Добавляем в историю
                self.history.append({"role": "user", "content": user_text})
                self.history.append({"role": "assistant", "content": content})
                
                recipe = Recipe.from_dict(res_data.get("recipe")) if res_data.get("recipe") else None
                return (res_data.get("message", ""), recipe)
            except:
                return (content, None)

    def reset_context(self):
        self.history = []
