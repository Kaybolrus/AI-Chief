# AI Chef Pro — структура проекта

```
ai_chef_pro/
├── main.py                  # точка входа Flet
├── config.py                # константы, API ключ
├── requirements.txt
│
├── core/
│   ├── __init__.py
│   ├── gemini_client.py     # Gemini API, JSON mode, context trim
│   ├── chat_controller.py   # логика диалога, history manager
│   └── recipe_state.py      # текущий рецепт, патчинг
│
├── data/
│   ├── __init__.py
│   ├── database.py          # SQLite: favorites, history, last_state
│   ├── models.py            # dataclasses: Recipe, Favorite, HistoryItem
│   └── export_import.py     # .json/.chef export/import, merge logic
│
├── ui/
│   ├── __init__.py
│   ├── app.py               # AppShell, навигация
│   ├── screens/
│   │   ├── home_screen.py   # главный экран, категории
│   │   ├── chat_screen.py   # чат + карточка рецепта
│   │   ├── favorites_screen.py
│   │   └── settings_screen.py
│   ├── components/
│   │   ├── recipe_card.py   # RecipeCard с таймерами
│   │   ├── timer_widget.py  # TimerButton с countdown
│   │   ├── message_bubble.py
│   │   └── quick_chips.py
│   └── theme.py             # цвета, тёмная тема
│
└── utils/
    ├── __init__.py
    ├── timer_engine.py      # countdown логика
    └── share_helper.py      # Android Share Sheet
```
