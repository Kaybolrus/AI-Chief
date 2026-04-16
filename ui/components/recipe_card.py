import flet as ft
from data.models import Recipe
from utils.timer_engine import TimerEngine

DIFF_COLORS = {
    "easy":   ("#052e16", "#4ade80"),
    "medium": ("#1c1500", "#fde68a"),
    "hard":   ("#450a0a", "#fca5a5"),
}

def build_timer_button(step_index, timer_sec, engine, page):
    timer_id = f"step_{step_index}"
    
    # Текст внутри кнопки
    label = ft.Text(
        f"⏱ {timer_sec // 60} мин",
        size=12,
        color="#fbbf24",
        weight=ft.FontWeight.W_600,
    )

    def on_tick(tid, remaining):
        m, s = divmod(remaining, 60)
        label.value = f"⏳ {m:02d}:{s:02d}"
        label.color = "#4ade80" if remaining > 30 else "#f87171"
        try:
            page.update()
        except:
            pass

    async def on_done(tid):
        label.value = "✅ ГОТОВО!"
        label.color = "#ffffff"
        btn.bgcolor = "#16a34a" # Зеленый успех
        
        # Уведомление пользователя
        page.snack_bar = ft.SnackBar(
            content=ft.Text(f"Таймер завершен: Шаг №{step_index + 1} готов!", color="#ffffff"),
            bgcolor="#16a34a",
            duration=4000
        )
        page.snack_bar.open = True
        
        try:
            page.haptic_feedback.heavy_impact()
        except:
            pass
        page.update()

    def handle_click(e):
        existing = engine.get(timer_id)
        if existing and existing.active:
            # Если таймер работает - останавливаем
            engine.cancel_timer(timer_id)
            label.value = f"⏱ {timer_sec // 60} мин"
            label.color = "#fbbf24"
            btn.bgcolor = "#1c1005"
            btn.border = ft.border.all(1, "#92400e")
        else:
            # Запускаем новый или перезапускаем
            btn.bgcolor = "#2a1505"
            btn.border = ft.border.all(1, "#fbbf24")
            engine.start_timer(timer_id, timer_sec, on_tick, on_done, page)
        page.update()

    btn = ft.Container(
        content=label,
        bgcolor="#1c1005",
        border=ft.border.all(1, "#92400e"),
        border_radius=8,
        padding=ft.padding.symmetric(horizontal=12, vertical=6),
        on_click=handle_click,
        ink=True,
        animate=ft.animation.Animation(300, ft.AnimationCurve.DECELERATE)
    )
    return btn

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
            border_radius=12, alignment=ft.alignment.center,
        )
        
        step_content = ft.Column([
            ft.Text(step.text, size=14, color="#e0e0e0", soft_wrap=True),
        ], spacing=6, expand=True)
        
        if step.timer_sec and step.timer_sec > 0:
            step_content.controls.append(
                ft.Row([build_timer_button(i, step.timer_sec, engine, page)])
            )

        steps_col.controls.append(
            ft.Row([num, step_content], vertical_alignment=ft.CrossAxisAlignment.START, spacing=12)
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
                        expand=True, border_radius=10, padding=12, on_click=on_save, alignment=ft.alignment.center
                    ),
                    ft.Container(
                        content=ft.Text("📤 Поделиться", color="#a8a09a"),
                        bgcolor="#1a1a1a", expand=True, border_radius=10, padding=12,
                        on_click=on_share, alignment=ft.alignment.center
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
