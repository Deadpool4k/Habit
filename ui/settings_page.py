"""Settings page — API key, model, reminders, export."""
import csv
import json
from datetime import date

import flet as ft

from config import load_config, save_config
import repositories.memory_repository as mem_repo
from database.database import get_connection

BG = "#0f172a"
CARD = "#1e293b"
ACCENT = "#6366f1"
SUCCESS = "#22c55e"
TEXT = "#f1f5f9"
DANGER = "#ef4444"

MODELS = ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]


class SettingsPage(ft.Column):
    """Application settings: API key, model, reminders, data export."""

    def __init__(self, flet_page: ft.Page):
        super().__init__(expand=True, spacing=0)
        self._page = flet_page
        self._config = load_config()
        self._api_ref = ft.Ref[ft.TextField]()
        self._model_ref = ft.Ref[ft.Dropdown]()
        self._reminder_ref = ft.Ref[ft.TextField]()

        self.controls = [
            ft.Container(
                bgcolor=CARD,
                padding=ft.padding.symmetric(horizontal=20, vertical=12),
                content=ft.Text("⚙️ Settings", color=TEXT, size=20, weight=ft.FontWeight.BOLD),
            ),
            ft.Container(
                expand=True,
                padding=16,
                content=ft.Column(
                    [
                        self._build_ai_section(),
                        self._build_reminder_section(),
                        self._build_data_section(),
                    ],
                    scroll=ft.ScrollMode.AUTO,
                    spacing=16,
                    expand=True,
                ),
            ),
        ]

    # ------------------------------------------------------------------
    def _build_ai_section(self) -> ft.Container:
        api_field = ft.TextField(
            ref=self._api_ref,
            label="OpenAI API Key",
            value=self._config.get("openai_api_key", ""),
            password=True,
            can_reveal_password=True,
            bgcolor=BG,
            color=TEXT,
            label_style=ft.TextStyle(color="#94a3b8"),
            border_color="#334155",
            focused_border_color=ACCENT,
            expand=True,
        )

        model_dd = ft.Dropdown(
            ref=self._model_ref,
            label="Model",
            value=self._config.get("openai_model", "gpt-4o"),
            options=[ft.dropdown.Option(m) for m in MODELS],
            bgcolor=BG,
            color=TEXT,
            label_style=ft.TextStyle(color="#94a3b8"),
            border_color="#334155",
            focused_border_color=ACCENT,
            width=200,
        )

        save_btn = ft.ElevatedButton(
            "Save Settings",
            bgcolor=ACCENT,
            color=TEXT,
            icon=ft.Icons.SAVE,
            on_click=self._on_save,
        )

        clear_btn = ft.OutlinedButton(
            "Clear Chat History",
            style=ft.ButtonStyle(color=DANGER, side=ft.BorderSide(1, DANGER)),
            on_click=self._on_clear_chat,
        )

        return ft.Container(
            bgcolor=CARD,
            border_radius=8,
            padding=16,
            content=ft.Column(
                [
                    ft.Text("AI Configuration", color=TEXT, size=15, weight=ft.FontWeight.BOLD),
                    ft.Row([api_field, model_dd], spacing=12),
                    ft.Row([save_btn, clear_btn], spacing=12),
                ],
                spacing=12,
            ),
        )

    def _build_reminder_section(self) -> ft.Container:
        reminder_field = ft.TextField(
            ref=self._reminder_ref,
            label="Daily Reminder Time (HH:MM)",
            value=self._config.get("reminder_time", "09:00"),
            bgcolor=BG,
            color=TEXT,
            label_style=ft.TextStyle(color="#94a3b8"),
            border_color="#334155",
            focused_border_color=ACCENT,
            width=200,
        )

        save_btn = ft.ElevatedButton(
            "Save Reminder",
            bgcolor=ACCENT,
            color=TEXT,
            icon=ft.Icons.ALARM,
            on_click=self._on_save,
        )

        return ft.Container(
            bgcolor=CARD,
            border_radius=8,
            padding=16,
            content=ft.Column(
                [
                    ft.Text("Notifications", color=TEXT, size=15, weight=ft.FontWeight.BOLD),
                    ft.Text(
                        "Set the time to receive your daily habit reminder.",
                        color="#94a3b8",
                        size=12,
                    ),
                    ft.Row([reminder_field, save_btn], spacing=12),
                ],
                spacing=10,
            ),
        )

    def _build_data_section(self) -> ft.Container:
        return ft.Container(
            bgcolor=CARD,
            border_radius=8,
            padding=16,
            content=ft.Column(
                [
                    ft.Text("Data Export", color=TEXT, size=15, weight=ft.FontWeight.BOLD),
                    ft.Text(
                        "Export your habit and journal data for backup or analysis.",
                        color="#94a3b8",
                        size=12,
                    ),
                    ft.Row(
                        [
                            ft.ElevatedButton(
                                "Export as JSON",
                                bgcolor="#1e293b",
                                color=TEXT,
                                icon=ft.Icons.DOWNLOAD,
                                on_click=self._on_export_json,
                                style=ft.ButtonStyle(side=ft.BorderSide(1, "#334155")),
                            ),
                            ft.ElevatedButton(
                                "Export as CSV",
                                bgcolor="#1e293b",
                                color=TEXT,
                                icon=ft.Icons.TABLE_CHART,
                                on_click=self._on_export_csv,
                                style=ft.ButtonStyle(side=ft.BorderSide(1, "#334155")),
                            ),
                        ],
                        spacing=12,
                    ),
                ],
                spacing=10,
            ),
        )

    # ------------------------------------------------------------------
    def _on_save(self, e):
        self._config["openai_api_key"] = self._api_ref.current.value.strip()
        self._config["openai_model"] = self._model_ref.current.value or "gpt-4o"
        reminder = (self._reminder_ref.current.value or "09:00").strip()
        self._config["reminder_time"] = reminder
        save_config(self._config)
        self._show_snack("Settings saved!")

    def _on_clear_chat(self, e):
        def do_clear(ev):
            mem_repo.clear_messages()
            self._page.close(dialog)
            self._show_snack("Chat history cleared.")

        def cancel(ev):
            self._page.close(dialog)

        dialog = ft.AlertDialog(
            title=ft.Text("Clear chat history?", color=TEXT),
            content=ft.Text("All conversation messages will be deleted.", color="#94a3b8"),
            bgcolor=CARD,
            actions=[
                ft.TextButton("Cancel", on_click=cancel),
                ft.ElevatedButton("Clear", bgcolor=DANGER, color=TEXT, on_click=do_clear),
            ],
        )
        self._page.open(dialog)

    def _on_export_json(self, e):
        conn = get_connection()
        habits = [dict(r) for r in conn.execute("SELECT * FROM habits").fetchall()]
        entries = [dict(r) for r in conn.execute("SELECT * FROM habit_entries").fetchall()]
        journals = [dict(r) for r in conn.execute("SELECT * FROM journal_entries").fetchall()]

        data = {"habits": habits, "habit_entries": entries, "journal_entries": journals}
        filename = f"habit_tracker_export_{date.today().isoformat()}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        self._show_snack(f"Exported to {filename}")

    def _on_export_csv(self, e):
        conn = get_connection()
        entries = conn.execute(
            """SELECT h.name, h.icon, he.date, he.value
               FROM habit_entries he
               JOIN habits h ON h.id = he.habit_id
               ORDER BY he.date, h.name"""
        ).fetchall()

        filename = f"habit_entries_export_{date.today().isoformat()}.csv"
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["habit_name", "icon", "date", "value"])
            for r in entries:
                writer.writerow([r["name"], r["icon"], r["date"], r["value"]])
        self._show_snack(f"Exported to {filename}")

    # ------------------------------------------------------------------
    def _show_snack(self, msg: str, error: bool = False):
        snack = ft.SnackBar(
            content=ft.Text(msg, color=TEXT),
            bgcolor=DANGER if error else SUCCESS,
        )
        self._page.open(snack)
