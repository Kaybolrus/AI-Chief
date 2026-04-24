import flet as ft
from data.models import Recipe
from utils.timer_engine import TimerEngine
# Импортируем нашу кнопку из нового файла
from ui.components.timer_logic import create_step_timer

DIFF_COLORS = {
    "easy":   ("#052e16", "#4ade80"),
    "medium": ("#1c1500", "#fde68a"),
    "hard":   ("#450a0a", "#fca5a5"),
}

def build_recipe_card(recipe, engine, page, on_save=None, on_share=None, is_saved=False):
    diff_bg, diff_fg = DIFF_COLORS.get(recipe.difficulty, ("#1a1a1a", "#aaa"))

    # Мета-данные
    meta = ft.Row([
        ft.Text(f"⏱ {recipe.time_min} мин", size=12, color="#a8a09a"),
        ft.Text(f"👤 {recipe.servings} порц.", size=12, color="#a8a09a"),
        ft.Text(f"🔥 {recipe.calories} ккал", size=12, color="#a8a09a"),
        ft.Container(
            content=ft.Text(recipe.difficulty_label(), size=10, weight="600", color=diff_fg),
            bgcolor=diff_bg, border_radius=12, padding=ft.padding.symmetric(horizontal=8, vertical=2),
        ),
    ], spacing=12, wrap=True)

    # Ингредиенты
    ing_chips = ft.Row([
        ft.Container(
            content=ft.Text(ing, size=12, color="#f5f0e8"),
            bgcolor="#1a1a1a", border=ft.border.all(0.5, "#2a2624"),
            border_radius=8, padding=ft.padding.symmetric(horizontal=10, vertical=5),
        ) for ing in recipe.ingredients
    ], spacing=6, wrap=True)

    # Шаги приготовления
    steps_col = ft.Column(spacing=12)
    for i, step in enumerate(recipe.steps):
        num = ft.Container(
            content=ft.Text(str(i + 1), size=11, weight="bold", color="#fbbf24"),
            width=24, height=24, bgcolor="#2a1505", border=ft.border.all(1, "#92400e"),
            border_radius=12, alignment=ft.alignment.Alignment(0, 0),
        )
        
        step_content = ft.Column([
            ft.Text(step.text, size=14, color="#e0e0e0", soft_wrap=True),
        ], spacing=6, expand=True)
        
        # Используем функцию из внешнего файла
        if step.timer_sec and step.timer_sec > 0:
            timer_widget = create_step_timer(i, step.timer_sec, engine, page)
            step_content.controls.append(ft.Row([timer_widget]))

        steps_col.controls.append(
            ft.Row([num, step_content], vertical_alignment="start", spacing=12)
        )

    # Сборка карточки
    return ft.Container(
        content=ft.Column([
            ft.Container(
                content=ft.Column([
                    ft.Text(recipe.title, size=20, weight="bold", color="#f5f0e8"),
                    meta,
                ], spacing=8),
                padding=20, border=ft.border.only(bottom=ft.BorderSide(0.5, "#2a2624")),
            ),
            _section("Ингредиенты", ing_chips),
            _section("Приготовление", steps_col),
            ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=ft.Text("✓ Сохранено" if is_saved else "💾 Сохранить", color="#4ade80" if is_saved else "#a8a09a"),
                        bgcolor="#052e16" if is_saved else "#1a1a1a",
                        expand=True, border_radius=10, padding=12, on_click=on_save, alignment=ft.alignment.Alignment(0, 0)
                    ),
                    ft.Container(
                        content=ft.Text("📤 Поделиться", color="#a8a09a"),
                        bgcolor="#1a1a1a", expand=True, border_radius=10, padding=12,
                        on_click=on_share, alignment=ft.alignment.Alignment(0, 0)
                    ),
                ], spacing=10),
                padding=20
            )
        ], spacing=0),
        bgcolor="#111111", border=ft.border.all(1, "#2a2624"), border_radius=20,
    )

def _section(label, content):
    return ft.Container(
        content=ft.Column([
            ft.Text(label.upper(), size=11, weight="bold", color="#5a5450", letter_spacing=1.2),
            content,
        ], spacing=12),
        padding=20, border=ft.border.only(bottom=ft.BorderSide(0.5, "#2a2624")),
    )
