import flet as ft
from data.database import Database
from core.gemini_client import GeminiClient
from core.chat_controller import ChatController
from ui.screens.chat_screen import ChatScreen
from ui.screens.favorites_screen import FavoritesScreen
from utils.timer_engine import TimerEngine


def main(page: ft.Page):
    # ── Базовые настройки ──────────────────────────────────────
    page.title = "AI Chef Pro"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0c0c0c"
    page.padding = 0
    page.fonts = {}

    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary="#D97706",
            secondary="#92400e",
            background="#0c0c0c",
            surface="#141414",
            on_primary="#0c0c0c",
        )
    )

    # ── Инициализация слоёв ────────────────────────────────────
    db = Database()
    gemini = GeminiClient()
    controller = ChatController(db, gemini)
    engine = TimerEngine()

    # ── Экраны ────────────────────────────────────────────────
    chat_screen    = ChatScreen(controller, engine, page)
    fav_screen     = FavoritesScreen(db, controller, engine, page)

    # ── Хедер ─────────────────────────────────────────────────
    def new_recipe(e):
        controller.start_new_recipe()
        chat_screen._messages.controls.clear()
        chat_screen._show_welcome()
        nav.selected_index = 0
        content.content = chat_screen
        page.update()

    header = ft.Container(
        content=ft.Row([
            ft.Row([
                ft.Container(
                    content=ft.Text("🍳", size=22),
                    width=38, height=38,
                    bgcolor="#2a1505",
                    border_radius=19,
                    alignment=ft.alignment.center,
                ),
                ft.Text("AI Chef Pro", size=17, weight=ft.FontWeight.W_700, color="#f5f0e8"),
            ], spacing=10),
            ft.Row([
                ft.Container(
                    content=ft.Text("➕", size=16),
                    width=36, height=36,
                    bgcolor="#1a1a1a",
                    border=ft.border.all(0.5, "#2a2624"),
                    border_radius=18,
                    alignment=ft.alignment.center,
                    on_click=new_recipe,
                    ink=True,
                    tooltip="Новый рецепт",
                ),
            ], spacing=8),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        bgcolor="#141414",
        padding=ft.padding.symmetric(horizontal=16, vertical=10),
        border=ft.border.only(bottom=ft.BorderSide(0.5, "#2a2624")),
    )

    # ── Навигация ──────────────────────────────────────────────
    content = ft.Container(content=chat_screen, expand=True)

    def on_nav(e):
        idx = e.control.selected_index
        if idx == 0:
            content.content = chat_screen
        elif idx == 1:
            fav_screen.refresh()
            content.content = fav_screen
        page.update()

    nav = ft.NavigationBar(
        bgcolor="#141414",
        indicator_color="#2a1505",
        destinations=[
            ft.NavigationBarDestination(
                icon=ft.icons.CHAT_BUBBLE_OUTLINE,
                selected_icon=ft.icons.CHAT_BUBBLE,
                label="Чат",
            ),
            ft.NavigationBarDestination(
                icon=ft.icons.STAR_BORDER,
                selected_icon=ft.icons.STAR,
                label="Избранное",
            ),
        ],
        on_change=on_nav,
    )

    page.add(
        ft.Column([
            header,
            content,
            nav,
        ], spacing=0, expand=True)
    )


ft.app(target=main)
