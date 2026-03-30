# AI Chef Pro

Мобильное приложение — AI-повар на Flet + Python + Gemini API.

## Быстрый старт

```bash
# 1. Установить зависимости
pip install -r requirements.txt

# 2. Задать API ключ
export GEMINI_API_KEY="ваш_ключ_из_aistudio.google.com"

# 3. Запустить на десктопе (для разработки)
python main.py

# 4. Собрать APK для Android
flet build apk
```

## Структура файлов

```
main.py                        # точка входа
config.py                      # API ключ, системный промпт, настройки

core/
  gemini_client.py             # Gemini API, JSON mode, trim контекста
  chat_controller.py           # логика диалога

data/
  models.py                    # Recipe, Favorite, HistoryItem
  database.py                  # SQLite: favorites, history, last_state
  export_import.py             # .json/.chef export/import + merge

ui/
  screens/
    chat_screen.py             # главный чат-экран
    favorites_screen.py        # экран избранного
  components/
    recipe_card.py             # карточка рецепта с таймерами

utils/
  timer_engine.py              # countdown таймеры (asyncio)
```

## Ключевые решения

### JSON mode
Gemini всегда возвращает `response_mime_type="application/json"`.
Ответ парсится автоматически — нет риска markdown-обёртки.

### Trim контекста
Чтобы не тратить токены, история диалога сжимается до:
- System prompt (в модели)
- Первый user-запрос
- Последний JSON рецепта от модели

### Таймеры
`TimerEngine` использует `asyncio.create_task` — работает внутри Flet
event loop. При завершении — вибрация через `page.haptic_feedback`.

### Экспорт/Импорт
- Формат: `.json` / `.chef` (алиас JSON)
- Режим Merge: сравнение через `hash(json_data)` — дубли не добавляются
- Android Share: через `page.set_clipboard` + системный шаринг

### Восстановление контекста
При старте приложения `ChatController` загружает `last_recipe` из SQLite
и инжектирует его в историю Gemini — пользователь может сразу писать
"добавь грибы" без повторного запроса.

## Получить Gemini API ключ

1. Зайди на https://aistudio.google.com/app/apikey
2. Создай ключ
3. Вставь в `config.py` или переменную окружения `GEMINI_API_KEY`
