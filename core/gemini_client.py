import json
import urllib.request
import urllib.error
import asyncio
import ssl
import certifi
from config import GROQ_API_KEY, SYSTEM_PROMPT
from data.models import Recipe
from typing import Optional

class GeminiClient:
    def __init__(self):
        # Очистка ключа от кавычек и лишних пробелов
        raw_key = str(GROQ_API_KEY).strip()
        self.api_key = raw_key.replace('"', '').replace("'", "").replace("\n", "").replace("\r", "").strip()
        
        # Эндпоинт OpenRouter
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        
        try:
            self.ssl_context = ssl.create_default_context(cafile=certifi.where())
        except Exception:
            self.ssl_context = None

    async def send_message(self, user_text: str) -> tuple[str, Optional[Recipe]]:
        # Проверка наличия ключа
        if not self.api_key or "YOUR_GROQ" in self.api_key or len(self.api_key) < 10:
            return ("Ошибка: API ключ OpenRouter не найден или некорректен.", None)

        # Список бесплатных моделей для отказоустойчивости
        models_to_try = [
            "google/gemini-2.0-flash-exp:free",
            "meta-llama/llama-3.3-70b-instruct:free",
            "mistralai/mistral-7b-instruct:free",
            "google/gemini-flash-1.5-8b-exp:free"
        ]

        last_error = ""

        for model_name in models_to_try:
            try:
                return await self._make_request(model_name, user_text)
            except urllib.error.HTTPError as e:
                error_text = e.read().decode('utf-8', 'ignore')
                last_error = f"HTTP {e.code}: {error_text}"
                # Если 401 или 403 — проблема с ключом, нет смысла пробовать другие модели
                if e.code in [401, 403]:
                    break
                continue
            except Exception as e:
                last_error = str(e)
                continue
        
        return (f"Ошибка API. Подробности: {last_error}", None)

    async def _make_request(self, model_name: str, user_text: str) -> tuple[str, Optional[Recipe]]:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text}
        ]

        # Подготовка данных
        payload_data = {
            "model": model_name,
            "messages": messages,
            "temperature": 0.7,
            "top_p": 1,
            "frequency_penalty": 0,
            "presence_penalty": 0
        }

        payload = json.dumps(payload_data).encode("utf-8")

        # Заголовки (OpenRouter очень привередлив к ним)
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/aichef-app-project", # Любой валидный URL
            "X-Title": "AIChefPro",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        req = urllib.request.Request(self.api_url, data=payload, headers=headers, method="POST")

        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None, 
            lambda: urllib.request.urlopen(req, context=self.ssl_context, timeout=40)
        )
        
        with response as resp:
            raw_response = resp.read().decode("utf-8")
            data_res = json.loads(raw_response)
            
            if "choices" not in data_res:
                error_msg = data_res.get('error', {}).get('message', 'Неизвестная ошибка API')
                raise Exception(error_msg)
            
            content = data_res["choices"][0]["message"]["content"]
            
            # Извлекаем JSON из ответа (на случай, если модель добавила лишний текст)
            try:
                clean_content = content.replace("```json", "").replace("```", "").strip()
                start_idx = clean_content.find('{')
                end_idx = clean_content.rfind('}') + 1
                if start_idx != -1:
                    clean_content = clean_content[start_idx:end_idx]
                
                data_json = json.loads(clean_content)
                recipe = Recipe.from_dict(data_json.get("recipe")) if data_json.get("recipe") else None
                return (data_json.get("message", "Рецепт готов!"), recipe)
            except Exception:
                # Если JSON не распарсился, возвращаем текст как есть
                return (content, None)

    def reset_context(self):
        """Очистка контекста (необязательно для текущей реализации)"""
        pass

    def inject_recipe_context(self, recipe: Recipe):
        """Инъекция контекста последнего рецепта (необязательно)"""
        pass
