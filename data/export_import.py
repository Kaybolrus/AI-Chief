import json
import datetime
import os
from typing import Literal
from data.models import Recipe, Favorite
from data.database import Database
from config import APP_ID, APP_VERSION


def export_data(db: Database) -> dict:
    """Формирует dict для экспорта в .json/.chef"""
    favs = db.get_favorites()
    return {
        "app_id": APP_ID,
        "version": APP_VERSION,
        "export_date": datetime.date.today().isoformat(),
        "favorites": [
            {
                "title": f.title,
                "json_data": f.json_data,
                "content_hash": f.content_hash,
                "added_at": f.added_at,
            }
            for f in favs
        ],
        "settings": {
            "theme": db.load_state("theme", "dark"),
            "language": "ru",
        },
    }


def export_to_file(db: Database, path: str) -> str:
    """Сохраняет экспорт в файл, возвращает путь."""
    data = export_data(db)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return path


def import_from_file(
    db: Database,
    path: str,
    mode: Literal["merge", "overwrite"] = "merge",
) -> dict:
    """
    Импортирует данные из файла.
    mode='merge'     — добавляет только новые (по content_hash)
    mode='overwrite' — полностью заменяет favorites
    Возвращает статистику: {"added": N, "skipped": N, "errors": [...]}
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if data.get("app_id") != APP_ID:
        raise ValueError(f"Неверный app_id: {data.get('app_id')}")

    stats = {"added": 0, "skipped": 0, "errors": []}

    if mode == "overwrite":
        # Удаляем все favorites
        for fav in db.get_favorites():
            db.remove_favorite(fav.id)

    existing_hashes = {f.content_hash for f in db.get_favorites()}

    for item in data.get("favorites", []):
        try:
            raw_dict = json.loads(item["json_data"])
            recipe = Recipe.from_dict(raw_dict)
            h = item.get("content_hash") or recipe.content_hash()

            if mode == "merge" and h in existing_hashes:
                stats["skipped"] += 1
                continue

            added = db.add_favorite(recipe)
            if added:
                stats["added"] += 1
            else:
                stats["skipped"] += 1
        except Exception as e:
            stats["errors"].append(str(e))

    return stats


def get_share_text(recipe: Recipe) -> str:
    """Текст для шаринга через Telegram/WhatsApp."""
    lines = [
        f"🍳 *{recipe.title}*",
        f"⏱ {recipe.time_min} мин  |  👤 {recipe.servings} порц.  |  🔥 {recipe.calories} ккал",
        f"Сложность: {recipe.difficulty_label()}",
        "",
        "📦 *Ингредиенты:*",
    ]
    for ing in recipe.ingredients:
        lines.append(f"  • {ing}")
    lines.append("")
    lines.append("👨‍🍳 *Приготовление:*")
    for i, step in enumerate(recipe.steps, 1):
        timer = f" ⏱{step.timer_sec//60} мин" if step.timer_sec else ""
        lines.append(f"  {i}. {step.text}{timer}")
    lines.append("")
    lines.append("Создано в AI Chef Pro 🤖")
    return "\n".join(lines)
