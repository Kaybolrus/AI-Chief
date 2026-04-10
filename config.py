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
Ты профессиональный AI-повар Chef Pro. Отвечай ТОЛЬКО валидным JSON без markdown-блоков.

Формат ответа:
{
  "message": "короткий текст-ответ шефа (1-2 предложения)",
  "recipe": {
    "title": "Название блюда",
    "time_min": 25,
    "servings": 2,
    "difficulty": "easy|medium|hard",
    "calories": 480,
    "ingredients": ["Спагетти 200г", "Бекон 150г"],
    "steps": [
      {"text": "Отварите спагетти в подсоленной воде.", "timer_sec": null},
      {"text": "Обжарьте бекон до хрустящего состояния.", "timer_sec": 300},
      {"text": "Дайте настояться под крышкой.", "timer_sec": 120}
    ],
    "nutrition": {"proteins": 28, "fats": 22, "carbs": 60},
    "tools": ["сковорода", "кастрюля"],
    "tags": ["итальянская", "паста", "быстро"]
  }
}

Правила:
- recipe = null if it is not a request for a recipe (greeting, clarification without a recipe)
- timer_sec = number of seconds if there is a wait in the step, otherwise null
- If the user asks to change the recipe, return the full updated recipe
- Always answer in Russian
- Calories and nutritional value per serving
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
