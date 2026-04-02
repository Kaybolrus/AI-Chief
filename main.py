import flet as ft


def main(page: ft.Page):
    page.title = "AI Chef Pro"
    page.bgcolor = "#0c0c0c"
    page.add(
        ft.Text("Привет! Приложение работает.", color="white", size=20)
    )


ft.app(target=main)
