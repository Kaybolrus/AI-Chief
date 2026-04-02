from dataclasses import dataclass, field
from typing import Optional
import json
import hashlib
import datetime


@dataclass
class RecipeStep:
    text: str
    timer_sec: Optional[int] = None


@dataclass
class Recipe:
    title: str
    time_min: int
    servings: int
    difficulty: str
    calories: int
    ingredients: list[str]
    steps: list[RecipeStep]
    nutrition: dict
    tools: list[str]
    tags: list[str]
    raw_json: dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, d: dict) -> "Recipe":
        steps = [
            RecipeStep(s["text"], s.get("timer_sec"))
            for s in d.get("steps", [])
        ]
        return cls(
            title=d.get("title", ""),
            time_min=d.get("time_min", 0),
            servings=d.get("servings", 2),
            difficulty=d.get("difficulty", "easy"),
            calories=d.get("calories", 0),
            ingredients=d.get("ingredients", []),
            steps=steps,
            nutrition=d.get("nutrition", {}),
            tools=d.get("tools", []),
            tags=d.get("tags", []),
            raw_json=d,
        )

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "time_min": self.time_min,
            "servings": self.servings,
            "difficulty": self.difficulty,
            "calories": self.calories,
            "ingredients": self.ingredients,
            "steps": [{"text": s.text, "timer_sec": s.timer_sec} for s in self.steps],
            "nutrition": self.nutrition,
            "tools": self.tools,
            "tags": self.tags,
        }

    def content_hash(self) -> str:
        s = json.dumps(self.to_dict(), sort_keys=True, ensure_ascii=False)
        return hashlib.md5(s.encode()).hexdigest()

    def difficulty_label(self) -> str:
        return {"easy": "Легко", "medium": "Средне", "hard": "Сложно"}.get(
            self.difficulty, self.difficulty
        )


@dataclass
class Favorite:
    id: Optional[int]
    title: str
    json_data: str
    content_hash: str
    added_at: str = field(
        default_factory=lambda: datetime.datetime.now().isoformat()
    )

    @property
    def recipe(self) -> Recipe:
        return Recipe.from_dict(json.loads(self.json_data))


@dataclass
class HistoryItem:
    id: Optional[int]
    title: str
    json_data: str
    created_at: str = field(
        default_factory=lambda: datetime.datetime.now().isoformat()
    )

    @property
    def recipe(self) -> Recipe:
        return Recipe.from_dict(json.loads(self.json_data))
