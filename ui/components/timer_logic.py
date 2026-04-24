import flet as ft
import asyncio

def create_step_timer(step_index, timer_sec, engine, page):
    """
    Создает визуальный элемент таймера для шага рецепта.
    Использует TimerEngine для фонового отсчета.
    """
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
        except Exception:
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
        except Exception:
            pass
        try:
            page.update()
        except Exception:
            pass

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
            # Запускаем новый
            btn.bgcolor = "#2a1505"
            btn.border = ft.border.all(1, "#fbbf24")
            engine.start_timer(timer_id, timer_sec, on_tick, on_done, page)
        try:
            page.update()
        except Exception:
            pass

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
