"""Main entry point for AI Habit & Mood Tracker application."""
import flet as ft
from database.database import init_db
from ui.sidebar import Sidebar
from ui.habits_page import HabitsPage
from ui.edit_habits_page import EditHabitsPage
from ui.journal_page import JournalPage
from ui.settings_page import SettingsPage
from notifications.reminder_service import ReminderService


def main(page: ft.Page):
    page.title = "AI Habit & Mood Tracker"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0f172a"
    page.padding = 0

    # Initialize DB
    init_db()

    # State
    current_page_ref = {"page": "habits"}
    content_area = ft.Ref[ft.Container]()

    def navigate(page_name: str):
        current_page_ref["page"] = page_name
        render_page(page_name)

    def render_page(page_name: str):
        if page_name == "habits":
            content = HabitsPage(page)
        elif page_name == "edit_habits":
            content = EditHabitsPage(page)
        elif page_name == "journal":
            content = JournalPage(page)
        elif page_name == "settings":
            content = SettingsPage(page)
        else:
            content = HabitsPage(page)

        content_area.current.content = content
        content_area.current.update()

        # Update sidebar selection using the direct Python reference
        sidebar.update_selection(page_name)

    sidebar = Sidebar(
        on_navigate=navigate,
        current_page="habits",
    )

    main_content = ft.Container(
        ref=content_area,
        content=HabitsPage(page),
        expand=True,
        bgcolor="#0f172a",
    )

    page.add(
        ft.Row(
            [sidebar, main_content],
            expand=True,
            spacing=0,
        )
    )

    # Start reminder service
    reminder = ReminderService()
    reminder.start()


if __name__ == "__main__":
    ft.app(target=main)
