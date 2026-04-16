import os
import certifi
os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()

import flet as ft

def main(page: ft.Page):
    page.title = "AI Chef Pro"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0c0c0c"
    page.padding = 0
    page.window_status_bar_color = "#141414"

    try:
        page.theme = ft.Theme(
            color_scheme=ft.ColorScheme(
                primary="#D97706",
                secondary="#92400e",
                surface="#141414",
                on_primary="#0c0c0c",
            )
        )

        from data.database import Database
        from core.gemini_client import GeminiClient
        from core.chat_controller import ChatController
        from ui.screens.chat_screen import ChatScreen
        from ui.screens.favorites_screen import FavoritesScreen
        from utils.timer_engine import TimerEngine

        db = Database()
        gemini = GeminiClient()
        controller = ChatController(db, gemini)
        engine = TimerEngine()

        chat_screen = ChatScreen(controller, engine, page)
        fav_screen = FavoritesScreen(db, controller, engine, page)

        content_area = ft.Container(content=chat_screen, expand=True)

        def new_recipe(e):
            controller.start_new_recipe()
            if hasattr(chat_screen, '_messages'):
                chat_screen._messages.controls.clear()
            
            from config import QUICK_SUGGESTIONS
            chat_screen._load_suggestions(QUICK_SUGGESTIONS)
            
            page.navigation_bar.selected_index = 0
            content_area.content = chat_screen
            page.update()

        header = ft.Container(
            content=ft.Row([
                ft.Row([
                    ft.Container(
                        content=ft.Text("🍳", size=22),
                        width=38, height=38,
                        bgcolor="#2a1505",
                        border_radius=19,
                        # ВОЗВРАЩАЕМ СТАБИЛЬНЫЙ СИНТАКСИС
                        alignment=ft.alignment.Alignment(0, 0), 
                    ),
                    ft.Text(
                        "AI Chef Pro",
                        size=17,
                        weight=ft.FontWeight.W_700,
                        color="#f5f0e8",
                    ),
                ], spacing=10),
                ft.Container(
                    content=ft.Text("➕", size=16),
                    width=36, height=36,
                    bgcolor="#1a1a1a",
                    border=ft.border.all(0.5, "#2a2624"),
                    border_radius=18,
                    # ВОЗВРАЩАЕМ СТАБИЛЬНЫЙ СИНТАКСИС
                    alignment=ft.alignment.Alignment(0, 0),
                    on_click=new_recipe,
                    ink=True,
                ),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            bgcolor="#141414",
            padding=ft.padding.only(left=16, right=16, top=44, bottom=10),
            border=ft.border.only(bottom=ft.BorderSide(0.5, "#2a2624")),
        )

        def on_nav_change(e):
            idx = int(e.control.selected_index)
            if idx == 0:
                content_area.content = chat_screen
            elif idx == 1:
                fav_screen.update_list()
                content_area.content = fav_screen
            page.update()

        page.navigation_bar = ft.NavigationBar(
            bgcolor="#141414",
            indicator_color="#2a1505",
            selected_index=0,
            destinations=[
                ft.NavigationBarDestination(
                    icon=ft.icons.CHAT_BUBBLE_OUTLINE,
                    selected_icon=ft.icons.CHAT_BUBBLE,
                    label="Чат",
                ),
                ft.NavigationBarDestination(
                    icon=ft.icons.STAR_OUTLINE,
                    selected_icon=ft.icons.STAR,
                    label="Избранное",
                ),
            ],
            on_change=on_nav_change,
        )

        page.add(
            ft.Column([
                header,
                content_area,
            ], spacing=0, expand=True)
        )

    except Exception:
        import traceback
        error_text = traceback.format_exc()
        page.add(ft.Text(f"Ошибка: {error_text}", color="red", size=10))
        page.update()

if __name__ == "__main__":
    ft.app(target=main)
