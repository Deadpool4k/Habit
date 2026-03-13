"""Sidebar navigation component."""
import flet as ft

BG = "#0f172a"
CARD = "#1e293b"
ACCENT = "#6366f1"
TEXT = "#f1f5f9"

NAV_ITEMS = [
    ("habits", "📅", "Habits"),
    ("edit_habits", "✏️", "Edit Habits"),
    ("journal", "📓", "Journal"),
    ("settings", "⚙️", "Settings"),
]


class Sidebar(ft.UserControl):
    """Left-side navigation panel."""

    def __init__(self, on_navigate, current_page: str = "habits", *, ref=None):
        super().__init__(ref=ref)
        self.on_navigate = on_navigate
        self.current_page = current_page
        self._item_refs: dict[str, ft.Ref] = {k: ft.Ref[ft.Container]() for k, _, _ in NAV_ITEMS}

    def build(self):
        logo = ft.Container(
            padding=ft.padding.only(left=16, top=20, bottom=16),
            content=ft.Column(
                [
                    ft.Text("🧠", size=28),
                    ft.Text(
                        "Habit\nTracker",
                        color=TEXT,
                        size=13,
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=4,
            ),
        )

        nav_buttons = [self._make_item(key, icon, label) for key, icon, label in NAV_ITEMS]

        return ft.Container(
            width=160,
            bgcolor=CARD,
            content=ft.Column(
                [logo, ft.Divider(color="#334155", height=1)] + nav_buttons,
                spacing=0,
            ),
            expand=False,
        )

    def _make_item(self, key: str, icon: str, label: str) -> ft.Container:
        is_selected = key == self.current_page

        def on_click(e, k=key):
            self.current_page = k
            self._refresh_items()
            self.on_navigate(k)

        return ft.Container(
            ref=self._item_refs[key],
            padding=ft.padding.symmetric(horizontal=16, vertical=12),
            bgcolor=ACCENT if is_selected else "transparent",
            border_radius=0,
            on_click=on_click,
            content=ft.Row(
                [
                    ft.Text(icon, size=18),
                    ft.Text(label, color=TEXT, size=13),
                ],
                spacing=10,
            ),
            ink=True,
        )

    def _refresh_items(self):
        """Rebuild navigation items to reflect the new selection."""
        for key, icon, label in NAV_ITEMS:
            ref = self._item_refs.get(key)
            if ref and ref.current:
                is_selected = key == self.current_page
                ref.current.bgcolor = ACCENT if is_selected else "transparent"
                ref.current.update()

    def update_selection(self, page_name: str):
        """Called externally to update the highlighted nav item."""
        self.current_page = page_name
        self._refresh_items()
