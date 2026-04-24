import flet as ft
from core.chat_controller import ChatController
from ui.components.recipe_card import build_recipe_card
from data.models import Recipe
from data.export_import import get_share_text
from utils.timer_engine import TimerEngine
from config import QUICK_SUGGESTIONS, RECIPE_EDIT_CHIPS

class ChatScreen(ft.Column):
    def __init__(self, controller: ChatController, engine: TimerEngine, pg: ft.Page):
        super().__init__(expand=True, spacing=0)
        self.ctrl = controller
        self.engine = engine
        self._pg = pg

        # Основной список сообщений
        self._messages = ft.Column(
            scroll="auto",
            expand=True, 
            spacing=15, 
            auto_scroll=True
        )
        
        # Ряд с чипсами (подсказками)
        # Исправлено: Режим скролла AUTO надежнее HIDDEN
        self._chips_row = ft.Row(
            wrap=False,
            scroll="auto",
            spacing=8,
        )
        
        # Поле ввода
        self._input = ft.TextField(
            hint_text="Напиши что хочешь приготовить...",
            border_radius=25,
            bgcolor="#1c1c1c",
            expand=True,
            on_submit=self._on_send,
            content_padding=ft.padding.symmetric(horizontal=20, vertical=15),
            border_color="#2a2624",
            focused_border_color="#D97706",
            text_size=14
        )

        self.ctrl.on_message(self._handle_message)
        self.ctrl.on_recipe(self._handle_recipe)
        self.ctrl.on_error(self._handle_error)

        self._build_ui()
        self._load_suggestions(QUICK_SUGGESTIONS)

    def _build_ui(self):
        # Контейнер для нижней части (чипсы + поле ввода)
        bottom_panel = ft.Container(
            content=ft.Column([
                ft.Container(content=self._chips_row, padding=ft.padding.only(bottom=5)),
                ft.Row([
                    self._input,
                    ft.IconButton(
                        icon="send",
                        bgcolor="#D97706", 
                        icon_color="#141414",
                        on_click=self._on_send,
                        ink=True,
                    )
                ], spacing=10)
            ], tight=True),
            padding=ft.padding.only(left=15, right=15, bottom=20, top=15),
            bgcolor="#141414",
            border=ft.border.only(top=ft.BorderSide(1, "#2a2624"))
        )
        
        self.controls = [
            ft.Container(
                content=self._messages, 
                expand=True,
                padding=ft.padding.only(left=15, right=15, top=20, bottom=10)
            ), 
            bottom_panel
        ]

    def _load_suggestions(self, suggestions):
        self._chips_row.controls.clear()
        for icon, text in suggestions:
            self._chips_row.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Text(icon, size=12),
                        ft.Text(text, size=12, color="#f5f0e8", weight=ft.FontWeight.W_500),
                    ], tight=True, spacing=5),
                    bgcolor="#1c1c1c",
                    border=ft.border.all(1, "#2a2624"),
                    border_radius=15,
                    padding=ft.padding.symmetric(horizontal=12, vertical=8),
                    on_click=lambda e, t=text: self._handle_chip_click(t),
                    ink=True,
                )
            )
        try: 
            self._pg.update()
        except Exception: 
            pass

    async def _handle_chip_click(self, text):
        self._add_user_bubble(text)
        await self.ctrl.send(text)

    def _add_user_bubble(self, text: str):
        limit = (self._pg.width or 400) * 0.75
        self._messages.controls.append(
            ft.Row([
                ft.Container(expand=True),
                ft.Container(
                    content=ft.Text(value=str(text), size=14, color="#f5f0e8", soft_wrap=True),
                    bgcolor="#D97706",
                    border_radius=ft.border_radius.only(top_left=18, top_right=18, bottom_left=18, bottom_right=4),
                    padding=ft.padding.symmetric(horizontal=16, vertical=12),
                    max_width=limit,
                )
            ], alignment="end")
        )
        try:
            self._pg.update()
        except Exception:
            pass

    def _add_ai_bubble(self, text: str):
        limit = (self._pg.width or 400) * 0.8
        self._messages.controls.append(
            ft.Row([
                ft.Container(
                    content=ft.Text("👨‍🍳", size=14),
                    width=30, height=30, bgcolor="#2a2624", border_radius=15,
                    alignment=ft.alignment.Alignment(0, 0),
                ),
                ft.Container(
                    content=ft.Text(value=str(text), size=14, color="#f5f0e8", soft_wrap=True),
                    bgcolor="#1c1c1c",
                    border=ft.border.all(1, "#2a2624"),
                    border_radius=ft.border_radius.only(top_left=4, top_right=18, bottom_left=18, bottom_right=18),
                    padding=ft.padding.symmetric(horizontal=16, vertical=12),
                    max_width=limit,
                ),
            ], spacing=8, vertical_alignment="start")
        )
        try:
            self._pg.update()
        except Exception:
            pass

    async def _on_send(self, e):
        val = self._input.value.strip()
        if not val: return
        self._input.value = ""
        self._add_user_bubble(val)
        await self.ctrl.send(val)

    def _handle_message(self, text): 
        self._add_ai_bubble(text)

    def _handle_error(self, err): self._add_ai_bubble(f"⚠️ {err}")

    def _handle_recipe(self, recipe: Recipe):
        self._load_suggestions(RECIPE_EDIT_CHIPS)
        card = build_recipe_card(recipe, self.engine, self._pg)
        self._messages.controls.append(ft.Row([card], alignment="start"))
        try:
            self._pg.update()
        except Exception:
            pass
