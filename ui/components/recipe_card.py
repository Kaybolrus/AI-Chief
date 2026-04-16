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
    label = ft.Text(
        f"⏱ {timer_sec // 60} мин",
        size=12,
        color="#fbbf24",
        weight=ft.FontWeight.W_600,
    )

    def on_tick(tid, remaining):
        m, s = divmod(remaining, 60)
        label.value = f"▶ {m:02d}:{s:02d}"
        label.color = "#4ade80" if remaining > 10 else "#f87171"
        try:
            page.update()
        except Exception:
            pass

    def on_done(tid):
        label.value = "✓ Готово!"
        label.color = "#4ade80"
        btn.bgcolor = "#052e16"
        btn.border = ft.border.all(1, "#16a34a")
        try:
            page.haptic_feedback.heavy_impact()
        except Exception:
            pass
        try:
            page.update()
        except Exception:
            pass

    def start_timer(e):
        existing = engine.get(timer_id)
        if existing and existing.active:
            engine.cancel_timer(timer_id)
            label.value = f"⏱ {timer_sec // 60} мин"
            label.color = "#fbbf24"
            btn.bgcolor = "#1c1005"
            btn.border = ft.border.all(1, "#92400e")
        else:
            engine.start_timer(timer_id, timer_sec, on_tick, on_done, page)
            btn.bgcolor = "#052e16"
            btn.border = ft.border.all(1, "#16a34a")
        page.update()

    btn = ft.Container(
        content=label,
        bgcolor="#1c1005",
        border=ft.border.all(1, "#92400e"),
        border_radius=6,
        padding=ft.padding.symmetric(horizontal=8, vertical=3),
        on_click=start_timer,
        ink=True,
    )
    return btn


def build_recipe_card(recipe, engine, page, on_save=None, on_share=None, is_saved=False):
    diff_bg, diff_fg = DIFF_COLORS.get(recipe.difficulty, ("#1a1a1a", "#aaa"))

    meta = ft.Row([
        ft.Text(f"⏱ {recipe.time_min} мин", size=12, color="#a8a09a"),
        ft.Text(f"👤 {recipe.servings} порц.", size=12, color="#a8a09a"),
        ft.Text(f"🔥 {recipe.calories} ккал", size=12, color="#a8a09a"),
        ft.Container(
            content=ft.Text(
                recipe.difficulty_label(), size=10,
                weight=ft.FontWeight.W_600, color=diff_fg
            ),
            bgcolor=diff_bg,
            border_radius=12,
            padding=ft.padding.symmetric(horizontal=8, vertical=2),
        ),
    ], spacing=8, wrap=True)

    ing_chips = ft.Row([
        ft.Container(
            content=ft.Text(ing, size=11, color="#a8a09a"),
            bgcolor="#1a1a1a",
            border=ft.border.all(0.5, "#2a2624"),
            border_radius=8,
            padding=ft.padding.symmetric(horizontal=8, vertical=4),
        )
        for ing in recipe.ingredients
    ], spacing=6, wrap=True)

    steps_col = ft.Column(spacing=8)
    for i, step in enumerate(recipe.steps):
        num = ft.Container(
            content=ft.Text(
                str(i + 1), size=10,
                weight=ft.FontWeight.W_700, color="#fbbf24"
            ),
            width=22, height=22,
            bgcolor="#1c1005",
            border=ft.border.all(1, "#92400e"),
            border_radius=11,
            alignment=ft.Alignment(0, 0),
        )
        if step.timer_sec:
            timer_btn = build_timer_button(i, step.timer_sec, engine, page)
            content = ft.Column([
                ft.Text(step.text, size=12, color="#a8a09a", no_wrap=False),
                ft.Row([timer_btn]),
            ], spacing=4, expand=True)
        else:
            content = ft.Text(step.text, size=12, color="#a8a09a", no_wrap=False, expand=True)

        steps_col.controls.append(
            ft.Row([num, content], spacing=8,
                   vertical_alignment=ft.CrossAxisAlignment.START)
        )

    sections = [
        ft.Container(
            content=ft.Column([
                ft.Text(recipe.title, size=16,
                        weight=ft.FontWeight.W_700, color="#f5f0e8", no_wrap=False),
                meta,
            ], spacing=6),
            padding=ft.padding.all(14),
            border=ft.border.only(bottom=ft.BorderSide(0.5, "#2a2624")),
        ),
        _section("Ингредиенты", ing_chips),
        _section("Приготовление", steps_col),
    ]

    n = recipe.nutrition
    if n:
        nu_row = ft.Row([
            _nu_chip("Б", n.get("proteins", "—"), "#3b82f6"),
            _nu_chip("Ж", n.get("fats", "—"), "#f97316"),
            _nu_chip("У", n.get("carbs", "—"), "#a78bfa"),
        ], spacing=8)
        sections.append(_section("КБЖУ (на порцию)", nu_row))

    if recipe.tags:
        tags_row = ft.Row([
            ft.Container(
                content=ft.Text(f"#{t}", size=10, color="#6b7280"),
                padding=ft.padding.symmetric(horizontal=6, vertical=2),
                bgcolor="#1a1a1a",
                border_radius=20,
            )
            for t in recipe.tags
        ], spacing=6, wrap=True)
        sections.append(ft.Container(
            content=tags_row,
            padding=ft.padding.symmetric(horizontal=14, vertical=8)
        ))

    save_btn = ft.Container(
        content=ft.Text("✓ Сохранено" if is_saved else "💾 Сохранить",
                        size=13, color="#4ade80" if is_saved else "#a8a09a",
                        text_align=ft.TextAlign.CENTER),
        bgcolor="#052e16" if is_saved else "#1a1a1a",
        border=ft.border.all(0.5, "#2a2624"),
        border_radius=10,
        padding=ft.padding.symmetric(horizontal=12, vertical=10),
        on_click=on_save,
        ink=True,
        expand=True,
    )
    share_btn = ft.Container(
        content=ft.Text("📤 Поделиться", size=13, color="#a8a09a",
                        text_align=ft.TextAlign.CENTER),
        bgcolor="#1a1a1a",
        border=ft.border.all(0.5, "#2a2624"),
        border_radius=10,
        padding=ft.padding.symmetric(horizontal=12, vertical=10),
        on_click=on_share,
        ink=True,
        expand=True,
    )
    sections.append(ft.Container(
        content=ft.Row([save_btn, share_btn], spacing=8),
        padding=ft.padding.all(12),
    ))

    return ft.Container(
        content=ft.Column(sections, spacing=0),
        bgcolor="#161616",
        border=ft.border.all(0.5, "#2a2624"),
        border_radius=16,
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
    )


def _section(label, content):
    return ft.Container(
        content=ft.Column([
            ft.Text(label.upper(), size=10, weight=ft.FontWeight.W_600,
                    color="#5a5450"),
            content,
        ], spacing=8),
        padding=ft.padding.all(14),
        border=ft.border.only(bottom=ft.BorderSide(0.5, "#2a2624")),
    )


def _nu_chip(label, value, color):
    return ft.Container(
        content=ft.Column([
            ft.Text(label, size=10, color=color, weight=ft.FontWeight.W_600),
            ft.Text(f"{value}г", size=13, color="#f5f0e8",
                    weight=ft.FontWeight.W_700),
        ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        bgcolor="#1a1a1a",
        border=ft.border.all(0.5, "#2a2624"),
        border_radius=10,
        padding=ft.padding.symmetric(horizontal=16, vertical=8),
        expand=True,
    )
