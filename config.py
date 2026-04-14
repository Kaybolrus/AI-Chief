import os

# API Настройки
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_API_KEY_HERE")
GEMINI_MODEL   = "gemini-2.0-flash-lite"

# База данных и ID
APP_VERSION    = 1.0
APP_ID         = "ai_chef_pro"
DB_NAME        = "chef.db"

# Контекст: количество хранимых пар диалога (кроме первого запроса)
MAX_HISTORY_PAIRS = 1

SYSTEM_PROMPT = """
Ты профессиональный AI-повар. Отвечай ТОЛЬКО валидным JSON без markdown.

Формат:
{
  "message": "короткий ответ шефа",
  "recipe": {
    "title": "Название",
    "time_min": 25,
    "servings": 2,
    "difficulty": "easy|medium|hard",
    "calories": 480,
    "ingredients": ["Ингредиент 200г"],
    "steps": [
      {"text": "Описание шага", "timer_sec": null}
    ],
    "nutrition": {"proteins": 28, "fats": 22, "carbs": 60},
    "tools": ["сковорода"],
    "tags": ["быстро"]
  }
}

Правила:
- recipe равен null если это не запрос рецепта
- timer_sec это секунды ожидания или null
- При просьбе изменить рецепт возвращай полный обновлённый рецепт
- Отвечай только на русском
- КБЖУ указывай на порцию
"""

QUICK_SUGGESTIONS = [
    ("🍝", "Карбонара"),
    ("⚡", "Быстрый ужин"),
    ("🥗", "Сделай ПП"),
    ("🍚", "Из курицы и риса"),
    ("🥚", "Из яиц"),
    ("🍲", "Что-нибудь сытное"),
]

RECIPE_EDIT_CHIPS = [
    ("🚀", "Сделай быстрее"),
    ("💰", "Сделай дешевле"),
    ("🥗", "Сделай ПП"),
    ("🔄", "Заменить ингредиенты"),
    ("➕", "На 2 порции больше"),
    ("🥛", "Без молочки"),
]
