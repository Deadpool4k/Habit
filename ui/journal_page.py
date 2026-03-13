"""Journal page — daily journal, mood, and AI chat."""
import threading
from datetime import date

import flet as ft

from models.journal_entry import JournalEntry
from services import journal_service, ai_service
import repositories.memory_repository as mem_repo
from config import load_config

BG = "#0f172a"
CARD = "#1e293b"
ACCENT = "#6366f1"
SUCCESS = "#22c55e"
USER_BUBBLE = "#312e81"
TEXT = "#f1f5f9"
DANGER = "#ef4444"

MOOD_EMOJIS = {1: "😔", 2: "😕", 3: "😐", 4: "🙂", 5: "😄"}


class JournalPage(ft.Column):
    """Daily journal entry with mood tracking and AI chat."""

    def __init__(self, flet_page: ft.Page):
        super().__init__(expand=True, spacing=0)
        self._page = flet_page
        self.current_date = date.today().isoformat()
        self.entry = journal_service.get_or_create_entry(self.current_date)
        self.selected_mood = self.entry.mood
        self._chat_messages: list[dict] = mem_repo.get_all_messages(limit=50)

        # Refs
        self._journal_ref = ft.Ref[ft.TextField]()
        self._stress_ref = ft.Ref[ft.Slider]()
        self._energy_ref = ft.Ref[ft.Slider]()
        self._chat_list_ref = ft.Ref[ft.Column]()
        self._chat_input_ref = ft.Ref[ft.TextField]()
        self._mood_row_ref = ft.Ref[ft.Row]()
        self._send_btn_ref = ft.Ref[ft.IconButton]()
        self._date_ref = ft.Ref[ft.Text]()
        self._thinking_bubble = None

        self.controls = [
            ft.Container(
                bgcolor=CARD,
                padding=ft.padding.symmetric(horizontal=20, vertical=12),
                content=ft.Row(
                    [
                        ft.Text("📓 Journal", color=TEXT, size=20, weight=ft.FontWeight.BOLD),
                        ft.Text(ref=self._date_ref, value=self.current_date, color="#94a3b8", size=13),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
            ),
            ft.Container(
                expand=True,
                padding=16,
                content=ft.Column(
                    [
                        self._build_journal_form(),
                        self._build_chat_section(),
                    ],
                    scroll=ft.ScrollMode.AUTO,
                    spacing=16,
                    expand=True,
                ),
            ),
        ]

    # ------------------------------------------------------------------
    def _build_journal_form(self) -> ft.Container:
        text_field = ft.TextField(
            ref=self._journal_ref,
            value=self.entry.text,
            multiline=True,
            min_lines=5,
            max_lines=10,
            hint_text="Write about your day…",
            bgcolor=BG,
            color=TEXT,
            hint_style=ft.TextStyle(color="#475569"),
            border_color="#334155",
            focused_border_color=ACCENT,
            expand=True,
        )

        mood_buttons = ft.Row(
            ref=self._mood_row_ref,
            controls=[self._mood_btn(v) for v in range(1, 6)],
            spacing=8,
        )

        stress_slider = ft.Slider(
            ref=self._stress_ref,
            value=self.entry.stress_level,
            min=1,
            max=5,
            divisions=4,
            label="{value}",
            active_color=ACCENT,
            thumb_color=ACCENT,
            expand=True,
        )

        energy_slider = ft.Slider(
            ref=self._energy_ref,
            value=self.entry.energy_level,
            min=1,
            max=5,
            divisions=4,
            label="{value}",
            active_color=SUCCESS,
            thumb_color=SUCCESS,
            expand=True,
        )

        save_btn = ft.ElevatedButton(
            "Save Entry",
            bgcolor=ACCENT,
            color=TEXT,
            icon=ft.Icons.SAVE,
            on_click=self._on_save,
        )

        return ft.Container(
            bgcolor=CARD,
            border_radius=8,
            padding=16,
            content=ft.Column(
                [
                    ft.Text("Today's Entry", color=TEXT, size=15, weight=ft.FontWeight.BOLD),
                    text_field,
                    ft.Text("Mood", color="#94a3b8", size=12),
                    mood_buttons,
                    ft.Row(
                        [
                            ft.Text("Stress:", color="#94a3b8", size=12, width=55),
                            stress_slider,
                        ]
                    ),
                    ft.Row(
                        [
                            ft.Text("Energy:", color="#94a3b8", size=12, width=55),
                            energy_slider,
                        ]
                    ),
                    save_btn,
                ],
                spacing=10,
            ),
        )

    def _mood_btn(self, value: int) -> ft.Container:
        is_selected = value == self.selected_mood
        emoji = MOOD_EMOJIS[value]

        def on_click(e, v=value):
            self.selected_mood = v
            self._refresh_mood_row()

        return ft.Container(
            width=52,
            height=52,
            border_radius=26,
            bgcolor=ACCENT if is_selected else "#334155",
            content=ft.Text(emoji, size=24, text_align=ft.TextAlign.CENTER),
            alignment=ft.alignment.Alignment(0, 0),
            on_click=on_click,
            ink=True,
            tooltip=f"Mood {value}",
        )

    def _refresh_mood_row(self):
        if self._mood_row_ref.current:
            self._mood_row_ref.current.controls = [self._mood_btn(v) for v in range(1, 6)]
            self._mood_row_ref.current.update()

    # ------------------------------------------------------------------
    def _build_chat_section(self) -> ft.Container:
        config = load_config()
        has_key = bool(config.get("openai_api_key", "").strip())

        if not has_key:
            warning = ft.Container(
                bgcolor=CARD,
                border_radius=8,
                padding=12,
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, color="#f59e0b"),
                        ft.Text(
                            "No OpenAI API key set. Visit Settings to enable AI chat.",
                            color="#94a3b8",
                            size=13,
                        ),
                    ],
                    spacing=8,
                ),
            )
        else:
            warning = ft.Container()

        chat_history = ft.Column(
            ref=self._chat_list_ref,
            controls=self._build_message_bubbles(),
            spacing=8,
            scroll=ft.ScrollMode.AUTO,
            height=300,
        )

        chat_input = ft.TextField(
            ref=self._chat_input_ref,
            hint_text="Ask your AI coach anything…",
            bgcolor=BG,
            color=TEXT,
            hint_style=ft.TextStyle(color="#475569"),
            border_color="#334155",
            focused_border_color=ACCENT,
            expand=True,
            on_submit=self._on_send,
        )

        send_btn = ft.IconButton(
            ref=self._send_btn_ref,
            icon=ft.Icons.SEND,
            icon_color=ACCENT,
            tooltip="Send",
            on_click=self._on_send,
            disabled=not has_key,
        )

        return ft.Container(
            bgcolor=CARD,
            border_radius=8,
            padding=16,
            content=ft.Column(
                [
                    ft.Text("🤖 AI Coach Chat", color=TEXT, size=15, weight=ft.FontWeight.BOLD),
                    warning,
                    chat_history,
                    ft.Row([chat_input, send_btn], spacing=8),
                ],
                spacing=10,
            ),
        )

    def _build_message_bubbles(self) -> list:
        bubbles = []
        for msg in self._chat_messages[-30:]:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            is_user = role == "user"
            bubble = ft.Container(
                bgcolor=USER_BUBBLE if is_user else CARD,
                border_radius=ft.border_radius.only(
                    top_left=12, top_right=12,
                    bottom_left=0 if is_user else 12,
                    bottom_right=12 if is_user else 0,
                ),
                padding=ft.padding.symmetric(horizontal=12, vertical=8),
                content=ft.Text(content, color=TEXT, size=13, selectable=True),
                alignment=ft.alignment.Alignment(1, 0) if is_user else ft.alignment.Alignment(-1, 0),
                margin=ft.margin.only(
                    left=60 if is_user else 0,
                    right=0 if is_user else 60,
                ),
            )
            bubbles.append(bubble)
        if not bubbles:
            bubbles.append(
                ft.Text("Start a conversation with your AI coach!", color="#475569", size=13)
            )
        return bubbles

    # ------------------------------------------------------------------
    def _on_save(self, e):
        self.entry.text = self._journal_ref.current.value or ""
        self.entry.mood = self.selected_mood
        self.entry.stress_level = int(self._stress_ref.current.value or 3)
        self.entry.energy_level = int(self._energy_ref.current.value or 3)
        journal_service.save_entry(self.entry)
        snack = ft.SnackBar(content=ft.Text("Journal entry saved!", color=TEXT), bgcolor=SUCCESS)
        self._page.snack_bar = snack
        self._page.snack_bar.open = True
        self._page.update()

    def _on_send(self, e):
        user_text = (self._chat_input_ref.current.value or "").strip()
        if not user_text:
            return

        # Clear input
        self._chat_input_ref.current.value = ""
        self._chat_input_ref.current.update()

        # Disable send button to prevent double sends
        if self._send_btn_ref.current:
            self._send_btn_ref.current.disabled = True
            self._send_btn_ref.current.update()

        # Add user message to local list and refresh chat
        self._chat_messages.append({"role": "user", "content": user_text})
        self._refresh_chat()

        # Add single thinking indicator AFTER refresh
        self._thinking_bubble = ft.Container(
            bgcolor=CARD,
            border_radius=8,
            padding=8,
            content=ft.Text("🤖 Thinking…", color="#94a3b8", size=12),
            margin=ft.margin.only(right=60),
        )
        if self._chat_list_ref.current:
            self._chat_list_ref.current.controls.append(self._thinking_bubble)
            self._chat_list_ref.current.update()

        def call_ai():
            reply = ai_service.send_message(user_text, self._page)
            self._chat_messages.append({"role": "assistant", "content": reply})
            # Remove thinking bubble
            if self._chat_list_ref.current and self._thinking_bubble in self._chat_list_ref.current.controls:
                try:
                    self._chat_list_ref.current.controls.remove(self._thinking_bubble)
                except ValueError:
                    pass
            self._refresh_chat()
            # Re-enable send button
            if self._send_btn_ref.current:
                self._send_btn_ref.current.disabled = False
                self._send_btn_ref.current.update()

        threading.Thread(target=call_ai, daemon=True).start()

    def _refresh_chat(self):
        if self._chat_list_ref.current:
            self._chat_list_ref.current.controls = self._build_message_bubbles()
            self._chat_list_ref.current.update()
