"""Journal page — mood tracking + AI coach chat."""
import threading
from datetime import date

import flet as ft

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
    """Mood tracker + AI coach chat. No journal text field."""

    def __init__(self, flet_page: ft.Page):
        super().__init__(expand=True, spacing=0)

        self._page = flet_page
        self.current_date = date.today().isoformat()

        self.entry = journal_service.get_or_create_entry(self.current_date)
        self.selected_mood = self.entry.mood

        self._chat_messages: list[dict] = mem_repo.get_all_messages(limit=50)
        self._thinking_bubble = None

        # Refs
        self._stress_ref = ft.Ref[ft.Slider]()
        self._energy_ref = ft.Ref[ft.Slider]()
        self._chat_list_ref = ft.Ref[ft.Column]()
        self._chat_input_ref = ft.Ref[ft.TextField]()
        self._mood_row_ref = ft.Ref[ft.Row]()
        self._send_btn_ref = ft.Ref[ft.IconButton]()

        config = load_config()
        self._has_key = bool(config.get("openai_api_key", "").strip())

        self.controls = [
            # Header
            ft.Container(
                bgcolor=CARD,
                padding=ft.padding.symmetric(horizontal=20, vertical=12),
                content=ft.Row(
                    [
                        ft.Text(
                            "📓 Journal",
                            color=TEXT,
                            size=20,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Text(self.current_date, color="#94a3b8", size=13),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
            ),

            # Mood / Stress / Energy card
            ft.Container(
                bgcolor=CARD,
                border_radius=8,
                padding=ft.padding.symmetric(horizontal=16, vertical=12),
                margin=ft.margin.only(left=16, right=16, top=12),
                content=ft.Column(
                    [
                        ft.Text("Mood", color="#94a3b8", size=12),

                        ft.Row(
                            ref=self._mood_row_ref,
                            controls=[self._mood_btn(v) for v in range(1, 6)],
                            spacing=8,
                        ),

                        ft.Row(
                            [
                                ft.Text("Stress:", color="#94a3b8", size=12, width=55),

                                ft.Slider(
                                    ref=self._stress_ref,
                                    value=self.entry.stress_level,
                                    min=1,
                                    max=5,
                                    divisions=4,
                                    label="{value}",
                                    active_color=ACCENT,
                                    thumb_color=ACCENT,
                                    expand=True,
                                ),
                            ]
                        ),

                        ft.Row(
                            [
                                ft.Text("Energy:", color="#94a3b8", size=12, width=55),

                                ft.Slider(
                                    ref=self._energy_ref,
                                    value=self.entry.energy_level,
                                    min=1,
                                    max=5,
                                    divisions=4,
                                    label="{value}",
                                    active_color=SUCCESS,
                                    thumb_color=SUCCESS,
                                    expand=True,
                                ),
                            ]
                        ),

                        ft.ElevatedButton(
                            "Save Mood",
                            bgcolor=ACCENT,
                            color=TEXT,
                            icon=ft.Icons.SAVE,
                            on_click=self._on_save_mood,
                        ),
                    ],
                    spacing=6,
                ),
            ),

            # AI Chat
            ft.Container(
                expand=True,
                padding=ft.padding.only(left=16, right=16, top=12, bottom=16),
                content=ft.Container(
                    bgcolor=CARD,
                    border_radius=8,
                    expand=True,
                    padding=16,
                    content=ft.Column(
                        [
                            ft.Text(
                                "🤖 AI Coach Chat",
                                color=TEXT,
                                size=14,
                                weight=ft.FontWeight.BOLD,
                            ),

                            ft.Column(
    ref=self._chat_list_ref,
    controls=self._build_message_bubbles(),
    spacing=8,
    scroll=ft.ScrollMode.AUTO,
    expand=True,
    auto_scroll=True,  # <-- ADAUGĂ ACEASTĂ LINIE
),

                            ft.Divider(color="#334155", height=1),

                            ft.Row(
                                [
                                    ft.TextField(
                                        ref=self._chat_input_ref,
                                        hint_text="Ask your AI coach anything…",
                                        bgcolor=BG,
                                        color=TEXT,
                                        hint_style=ft.TextStyle(color="#475569"),
                                        border_color="#334155",
                                        focused_border_color=ACCENT,
                                        expand=True,
                                        on_submit=self._on_send,
                                    ),

                                    ft.IconButton(
                                        ref=self._send_btn_ref,
                                        icon=ft.Icons.SEND,
                                        icon_color=ACCENT,
                                        tooltip="Send",
                                        on_click=self._on_send,
                                        disabled=not self._has_key,
                                    ),
                                ],
                                spacing=8,
                            ),
                        ],
                        spacing=8,
                        expand=True,
                    ),
                ),
            ),
        ]

    # ─────────────────────────────────────────────

    def _mood_btn(self, value: int) -> ft.Container:
        is_selected = value == self.selected_mood
        emoji = MOOD_EMOJIS[value]

        def on_click(e, v=value):
            self.selected_mood = v
            self._refresh_mood_row()

        return ft.Container(
            width=48,
            height=48,
            border_radius=24,
            bgcolor=ACCENT if is_selected else "#334155",
            content=ft.Text(emoji, size=22, text_align=ft.TextAlign.CENTER),
            alignment=ft.Alignment(0, 0),
            on_click=on_click,
            ink=True,
        )

    def _refresh_mood_row(self):
        if self._mood_row_ref.current:
            self._mood_row_ref.current.controls = [
                self._mood_btn(v) for v in range(1, 6)
            ]
            self._mood_row_ref.current.update()

    def _build_message_bubbles(self):

        bubbles = []

        for msg in self._chat_messages[-50:]:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            is_user = role == "user"

            bubble = ft.Container(
                bgcolor=USER_BUBBLE if is_user else "#273549",
                border_radius=12,
                padding=8,
                content=ft.Text(content, color=TEXT, size=13),
                alignment=ft.Alignment(1, 0) if is_user else ft.Alignment(-1, 0),
            )

            bubbles.append(bubble)

        return bubbles

    async def _scroll_to_bottom(self):
        """Scroll chat to bottom."""
        col = self._chat_list_ref.current
        if col:
            try:
                await col.scroll_to_async(offset=-1)
            except Exception:
                pass

    # ─────────────────────────────────────────────

    def _on_save_mood(self, e):
        """Save mood, stress, energy."""

        self.entry.mood = self.selected_mood
        self.entry.stress_level = int(self._stress_ref.current.value or 3)
        self.entry.energy_level = int(self._energy_ref.current.value or 3)

        journal_service.save_entry(self.entry)

        snack = ft.SnackBar(
            content=ft.Text("Mood saved!", color=TEXT),
            bgcolor=SUCCESS,
        )

        self._page.snack_bar = snack
        self._page.snack_bar.open = True
        self._page.update()

    # ─────────────────────────────────────────────

    def _on_send(self, e):

        user_text = (self._chat_input_ref.current.value or "").strip()

        if not user_text:
            return

        self._chat_input_ref.current.value = ""
        self._chat_input_ref.current.update()

        self._chat_messages.append(
            {"role": "user", "content": user_text}
        )

        self._refresh_chat()

        def call_ai():

            reply = ai_service.send_message(user_text, self._page)

            self._chat_messages.append(
                {"role": "assistant", "content": reply}
            )

            self._refresh_chat()

        threading.Thread(target=call_ai, daemon=True).start()

    def _refresh_chat(self):
        if self._chat_list_ref.current:
            self._chat_list_ref.current.controls = self._build_message_bubbles()
            self._chat_list_ref.current.update()