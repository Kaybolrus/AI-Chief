import flet as ft
from core.chat_controller import ChatController
from ui.components.recipe_card import build_recipe_card
from data.models import Recipe
from data.export_import import get_share_text
from utils.timer_engine import TimerEngine
from config import QUICK_SUGGESTIONS, RECIPE_EDIT_CHIPS


class ChatScreen(ft.Column):
    def __init__(self, controller: ChatController, engine: TimerEngine, page: ft.Page):
        super().__init__(expand=True, spacing=0)
        self.ctrl = controller
        self.engine = engine
        self.page = page

        # UI элементы
        self._messages = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=8,
            auto_scroll=True,
        )
        self._input = ft.TextField(
            hint_text="Напиши что хочешь приготовить...",
            border_radius=22,
            bgcolor="#1c1c1c",
            border_color="#2a2624",
            focused_border_color="#D97706",
            color="#f5f0e8",
            hint_style=ft.TextStyle(color="#5a5450"),
            expand=True,
            on_submit=self._on_send,
            text_size=14,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
        )
        self._typing_indicator = None

        # Подключаем колбэки
        self.ctrl.on_message(self._handle_message)
        self.ctrl.on_recipe(self._handle_recipe)
        self.ctrl.on_error(self._handle_error)

        self._build_ui()

        # Показываем приветствие
        if not self.ctrl.current_recipe:
            self._show_welcome()

    def _build_ui(self):
        input_row = ft.Container(
            content=ft.Row([
                self._input,
                ft.Container(
                    content=ft.Text("➤", size=16, color="#0c0c0c"),
                    width=42, height=42,
                    bgcolor="#D97706",
                    border_radius=21,
                    alignment=ft.alignment.center,
                    on_click=self._on_send,
                    ink=True,
                ),
            ], spacing=8),
            padding=ft.padding.symmetric(horizontal=12, vertical=10),
            bgcolor="#141414",
            border=ft.border.only(top=ft.BorderSide(0.5, "#2a2624")),
        )

        self.controls = [
            ft.Container(content=self._messages, expand=True, padding=ft.padding.all(10)),
            input_row,
        ]

    def _show_welcome(self):
        self._add_ai_bubble("Привет! Я твой AI-повар 🍳\nЧто приготовим сегодня?")
        chips = ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Text(f"{e} {t}", size=12, color="#a8a09a"),
                        bgcolor="#1c1c1c",
                        border=ft.border.all(0.5, "#2a2624"),
                        border_radius=20,
                        padding=ft.padding.symmetric(horizontal=10, vertical=6),
                        on_click=lambda ev, txt=t: self._quick_send(txt),
                        ink=True,
                    )
                    for e, t in QUICK_SUGGESTIONS
                ],
                spacing=8,
                wrap=True,
            ),
            padding=ft.padding.only(left=40, bottom=4),
        )
        self._messages.controls.append(chips)
        if self.page:
            self.page.update()

    def _add_user_bubble(self, text: str):
        self._messages.controls.append(
            ft.Row([
                ft.Container(expand=True),
                ft.Container(
                    content=ft.Text(text, size=13, color="#e0f0ff"),
                    bgcolor="#1e3a5f",
                    border=ft.border.all(0.5, "#1e4080"),
                    border_radius=ft.border_radius.only(
                        top_left=16, top_right=16, bottom_left=16, bottom_right=4
                    ),
                    padding=ft.padding.symmetric(horizontal=12, vertical=9),
                    max_width=240,
                ),
            ], spacing=8)
        )
        self.page.update()

    def _add_ai_bubble(self, text: str):
        self._messages.controls.append(
            ft.Row([
                ft.Container(
                    content=ft.Text("🍳", size=20),
                    width=34, height=34,
                    bgcolor="#2a1505",
                    border_radius=17,
                    alignment=ft.alignment.center,
                ),
                ft.Container(
                    content=ft.Text(text, size=13, color="#f5f0e8"),
                    bgcolor="#1c1c1c",
                    border=ft.border.all(0.5, "#2a2624"),
                    border_radius=ft.border_radius.only(
                        top_left=4, top_right=16, bottom_left=16, bottom_right=16
                    ),
                    padding=ft.padding.symmetric(horizontal=12, vertical=9),
                    max_width=260,
                ),
            ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.END)
        )
        self.page.update()

    def _add_typing_indicator(self):
        dots = ft.Row(
            [ft.Container(width=6, height=6, bgcolor="#5a5450", border_radius=3) for _ in range(3)],
            spacing=4,
        )
        self._typing_indicator = ft.Row([
            ft.Container(
                content=ft.Text("🍳", size=20),
                width=34, height=34,
                bgcolor="#2a1505",
                border_radius=17,
                alignment=ft.alignment.center,
            ),
            ft.Container(
                content=dots,
                bgcolor="#1c1c1c",
                border=ft.border.all(0.5, "#2a2624"),
                border_radius=16,
                padding=ft.padding.symmetric(horizontal=14, vertical=10),
            ),
        ], spacing=8)
        self._messages.controls.append(self._typing_indicator)
        self.page.update()

    def _remove_typing_indicator(self):
        if self._typing_indicator and self._typing_indicator in self._messages.controls:
            self._messages.controls.remove(self._typing_indicator)
            self._typing_indicator = None

    def _handle_message(self, text: str):
        self._remove_typing_indicator()
        self._add_ai_bubble(text)

    def _handle_recipe(self, recipe: Recipe):
        self._remove_typing_indicator()
        is_saved = self.ctrl.is_current_favorite()

        def on_save(e):
            ok = self.ctrl.save_current_to_favorites()
            if ok:
                e.control.text = "✓ Сохранено"
                e.control.bgcolor = "#052e16"
                e.control.color = "#4ade80"
                self.page.update()

        def on_share(e):
            share_text = get_share_text(recipe)
            self.page.set_clipboard(share_text)
            self._add_ai_bubble("Рецепт скопирован! Вставь в Telegram или WhatsApp 📤")

        card = build_recipe_card(
            recipe, self.engine, self.page,
            on_save=on_save, on_share=on_share, is_saved=is_saved
        )
        self._messages.controls.append(card)

        # Чипсы для редактирования рецепта
        edit_chips = ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Text(f"{e} {t}", size=11, color="#a8a09a"),
                        bgcolor="#1c1c1c",
                        border=ft.border.all(0.5, "#2a2624"),
                        border_radius=20,
                        padding=ft.padding.symmetric(horizontal=8, vertical=5),
                        on_click=lambda ev, txt=t: self._quick_send(txt),
                        ink=True,
                    )
                    for e, t in RECIPE_EDIT_CHIPS
                ],
                spacing=6,
                wrap=True,
            ),
            padding=ft.padding.only(left=42, top=4),
        )
        self._messages.controls.append(edit_chips)
        self.page.update()

    def _handle_error(self, error: str):
        self._remove_typing_indicator()
        self._add_ai_bubble(f"Ошибка: {error} 😔\nПопробуй ещё раз.")

    async def _on_send(self, e):
        text = self._input.value.strip()
        if not text:
            return
        self._input.value = ""
        self.page.update()
        self._add_user_bubble(text)
        self._add_typing_indicator()
        await self.ctrl.send(text)

    def _quick_send(self, text: str):
        self._input.value = text
        self.page.run_task(self._on_send, None)
