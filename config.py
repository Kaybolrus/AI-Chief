import os

# --- API Настройки (OpenRouter) ---
# Ключ от OpenRouter (может называться GROQ_API_KEY в твоих секретах GitHub)
OPENROUTER_API_KEY = os.getenv("GROQ_API_KEY", "YOUR_GROQ_KEY_HERE")

# Список моделей для перебора (если первая перегружена, включится вторая)
MODELS_PRIORITY = [
    "google/gemini-2.0-flash-exp",
    "meta-llama/llama-3.3-70b-instruct",
    "mistralai/mistral-7b-instruct",
    "google/gemini-flash-1.5-8b-exp"
]

# --- Параметры приложения ---
APP_VERSION = 1.2
APP_ID = "ai_chef_pro"
DB_NAME = "chef.db"

# Увеличенная память: бот помнит до 10 последних сообщений
MAX_HISTORY_PAIRS = 5 

# --- Оптимизированный системный промпт ---
SYSTEM_PROMPT = """
Ты профессиональный AI-повар. Отвечай СТРОГО в формате JSON.
Твоя задача — вести кулинарный диалог, учитывая историю сообщений. 
Если пользователь просит изменить текущее блюдо, проанализируй предыдущий рецепт и выдай обновленный.

JSON Format:
{
  "message": "короткий комментарий шефа",
  "recipe": {
    "title": "Название",
    "time_min": 25,
    "servings": 2,
    "difficulty": "easy|medium|hard",
    "calories": 480,
    "ingredients": ["Продукт 100г"],
    "steps": [
      {"text": "Описание", "timer_sec": null}
    ],
    "nutrition": {"proteins": 20, "fats": 15, "carbs": 40},
    "tools": ["нож"],
    "tags": ["ужин"]
  }
}
Правила:
- recipe = null, если это не запрос рецепта.
- timer_sec = секунды ожидания (если есть), иначе null.
- Всегда отвечай только на русском языке.
"""

# Быстрые предложения в чате
QUICK_SUGGESTIONS = [
    ("🍝", "Карбонара"), ("⚡", "Быстрый ужин"), ("🥗", "Сделай ПП"),
    ("🍚", "Из курицы и риса"), ("🥚", "Из яиц"), ("🍲", "Сытное")
]

# Кнопки под рецептом
RECIPE_EDIT_CHIPS = [
    ("🚀", "Быстрее"), ("💰", "Дешевле"), ("🥗", "ПП версия"),
    ("🔄", "Заменить продукты"), ("➕", "Больше порций"), ("🥛", "Без лактозы")
]
