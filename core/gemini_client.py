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
        # Используем ключ OpenRouter (в GitHub Secrets имя остается GROQ_API_KEY для удобства)
        self.api_key = str(GROQ_API_KEY).replace('"', '').replace("'", "").strip()
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        
        # Настройка SSL сертификатов для стабильности на Android
        try:
            self.ssl_context = ssl.create_default_context(cafile=certifi.where())
        except Exception:
            self.ssl_context = None

    async def send_message(self, user_text: str) -> tuple[str, Optional[Recipe]]:
        # Проверка наличия ключа
        if "YOUR_GROQ" in self.api_key or len(self.api_key) < 10:
            return ("Ошибка: API ключ OpenRouter не настроен.", None)

        # Список бесплатных моделей OpenRouter (всегда :free в конце)
        # 1. google/gemini-2.0-flash-exp:free (рекомендую, самая быстрая)
        # 2. meta-llama/llama-3.3-70b-instruct:free (очень мощная)
        model_name = "google/gemini-2.0-flash-exp:free"

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text}
        ]

        payload = json.dumps({
            "model": model_name,
            "messages": messages,
            "temperature": 0.7,
            "response_format": {"type": "json_object"}
        }).encode("utf-8")

        # Обязательные заголовки для работы с OpenRouter
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/aichef", # Любой валидный URL
            "X-Title": "AI Chef Pro",
            "User-Agent": "Mozilla/5.0 (Linux; Android 10)"
        }

        req = urllib.request.Request(self.api_url, data=payload, headers=headers, method="POST")

        try:
            loop = asyncio.get_event_loop()
            # Выполняем запрос
            response = await loop.run_in_executor(
                None, 
                lambda: urllib.request.urlopen(req, context=self.ssl_context, timeout=45)
            )
            
            with response as resp:
                result = json.loads(resp.read().decode("utf-8"))
                
                if "choices" not in result:
                    error_info = result.get('error', {}).get('message', 'Неизвестная ошибка')
                    return (f"OpenRouter Error: {error_info}", None)
                
                content = result["choices"][0]["message"]["content"]
                
                # Очистка контента от Markdown (бывает, что модели добавляют ```json)
                content = content.replace("```json", "").replace("```", "").strip()
                data = json.loads(content)
                
                recipe = Recipe.from_dict(data.get("recipe")) if data.get("recipe") else None
                return (data.get("message", "Ваш рецепт готов!"), recipe)

        except urllib.error.HTTPError as e:
            try:
                err_data = e.read().decode('utf-8')
                return (f"Ошибка {e.code}: {err_data[:100]}", None)
            except:
                return (f"Ошибка {e.code}: Доступ ограничен.", None)
        except Exception as e:
            return (f"Ошибка соединения: {str(e)}", None)

    def reset_context(self):
        """Сброс контекста диалога."""
        pass

    def inject_recipe_context(self, recipe: Recipe):
        """Инъекция контекста последнего рецепта."""
        pass
