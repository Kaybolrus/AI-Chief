import flet as ft
from data.database import Database
from data.models import Favorite
from core.chat_controller import ChatController
from ui.components.recipe_card import build_recipe_card
from utils.timer_engine import TimerEngine
from data.export_import import export_to_file, import_from_file
import os, tempfile


class FavoritesScreen(ft.Column):
    def __init__(self, db: Database, ctrl: ChatController, engine: TimerEngine, page: ft.Page):
        super().__init__(expand=True, spacing=0)
        self.db = db
        self.ctrl = ctrl
        self.engine = engine
        self.page = page
        self._list = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=8)
        self._build_ui()

    def _build_ui(self):
        toolbar = ft.Container(
            content=ft.Row([
                ft.Text("Избранное", size=16, weight=ft.FontWeight.W_700, color="#f5f0e8", expand=True),
                ft.TextButton(
                    "📤 Экспорт",
                    on_click=self._export,
                    style=ft.ButtonStyle(color="#D97706"),
                ),
                ft.TextButton(
                    "📥 Импорт",
                    on_click=self._import,
                    style=ft.ButtonStyle(color="#a8a09a"),
                ),
            ]),
            padding=ft.padding.symmetric(horizontal=16, vertical=10),
            border=ft.border.only(bottom=ft.BorderSide(0.5, "#2a2624")),
        )
        self.controls = [
            toolbar,
            ft.Container(content=self._list, expand=True, padding=ft.padding.all(10)),
        ]

    def refresh(self):
        self._list.controls.clear()
        favs = self.db.get_favorites()
        if not favs:
            self._list.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text("🍽", size=40, text_align=ft.TextAlign.CENTER),
                        ft.Text("Нет сохранённых рецептов", color="#5a5450", size=14),
                        ft.Text("Сохраняй рецепты из чата", color="#3a3432", size=12),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                    alignment=ft.alignment.center,
                    expand=True,
                    padding=ft.padding.only(top=80),
                )
            )
        else:
            for fav in favs:
                self._add_fav_item(fav)
        if self.page:
            self.page.update()

    def _add_fav_item(self, fav: Favorite):
        recipe = fav.recipe

        def on_remove(e, fid=fav.id):
            self.db.remove_favorite(fid)
            self.refresh()

        def on_share(e):
            from data.export_import import get_share_text
            self.page.set_clipboard(get_share_text(recipe))

        card = build_recipe_card(
            recipe, self.engine, self.page,
            on_save=on_remove,
            on_share=on_share,
            is_saved=True,
        )
        # Перезаписываем кнопку сохранить → удалить
        self._list.controls.append(card)

    def _export(self, e):
        try:
            tmp = os.path.join(tempfile.gettempdir(), "ai_chef_export.json")
            export_to_file(self.db, tmp)
            self.page.set_clipboard(f"Экспорт сохранён: {tmp}")
            self._snack("✅ Экспорт готов! Путь скопирован.")
        except Exception as ex:
            self._snack(f"Ошибка экспорта: {ex}")

    def _import(self, e):
        # Для Android: через file picker
        fp = ft.FilePicker(on_result=self._on_file_picked)
        self.page.overlay.append(fp)
        self.page.update()
        fp.pick_files(allowed_extensions=["json", "chef"])

    def _on_file_picked(self, e: ft.FilePickerResultEvent):
        if not e.files:
            return
        path = e.files[0].path
        try:
            stats = import_from_file(self.db, path, mode="merge")
            self._snack(f"✅ Импорт: добавлено {stats['added']}, пропущено {stats['skipped']}")
            self.refresh()
        except Exception as ex:
            self._snack(f"Ошибка импорта: {ex}")

    def _snack(self, msg: str):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(msg, color="#f5f0e8"),
            bgcolor="#1c1c1c",
        )
        self.page.snack_bar.open = True
        self.page.update()
