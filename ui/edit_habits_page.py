"""Edit Habits page — add, edit, and delete habits."""
import flet as ft

from models.habit import Habit
from services import habit_service

BG = "#0f172a"
CARD = "#1e293b"
ACCENT = "#6366f1"
SUCCESS = "#22c55e"
TEXT = "#f1f5f9"
DANGER = "#ef4444"

HABIT_TYPES = ["YES_NO", "COUNTER", "TIMER", "MEASURABLE"]
COLOR_OPTIONS = [
    "#6366f1", "#22c55e", "#ef4444", "#f59e0b",
    "#06b6d4", "#ec4899", "#8b5cf6", "#14b8a6",
]
ICON_OPTIONS = ["⭐", "💪", "📚", "🏃", "💧", "🧘", "🎯", "🍎", "😴", "✍️", "🎵", "🌱"]


class EditHabitsPage(ft.UserControl):
    """Page for managing (add / edit / delete) habits."""

    def __init__(self, page: ft.Page):
        super().__init__(expand=True)
        self.page = page
        self._editing: Habit | None = None
        self._build_form_refs()

    def _build_form_refs(self):
        self._name_ref = ft.Ref[ft.TextField]()
        self._type_ref = ft.Ref[ft.Dropdown]()
        self._icon_ref = ft.Ref[ft.Dropdown]()
        self._color_ref = ft.Ref[ft.Dropdown]()
        self._target_ref = ft.Ref[ft.TextField]()
        self._unit_ref = ft.Ref[ft.TextField]()
        self._list_ref = ft.Ref[ft.Column]()

    def build(self):
        return ft.Column(
            [
                ft.Container(
                    bgcolor=CARD,
                    padding=ft.padding.symmetric(horizontal=20, vertical=12),
                    content=ft.Text("✏️ Edit Habits", color=TEXT, size=20, weight=ft.FontWeight.BOLD),
                ),
                ft.Container(
                    expand=True,
                    padding=16,
                    content=ft.Column(
                        [
                            self._build_form(),
                            ft.Divider(color="#334155"),
                            ft.Text("Your Habits", color=TEXT, size=16, weight=ft.FontWeight.BOLD),
                            ft.Column(ref=self._list_ref, controls=self._build_habit_list(), spacing=8),
                        ],
                        scroll=ft.ScrollMode.AUTO,
                        spacing=16,
                        expand=True,
                    ),
                ),
            ],
            expand=True,
            spacing=0,
        )

    # ------------------------------------------------------------------
    def _build_form(self) -> ft.Container:
        title = "Edit Habit" if self._editing else "Add New Habit"

        name_field = ft.TextField(
            ref=self._name_ref,
            label="Habit Name",
            value=self._editing.name if self._editing else "",
            bgcolor="#0f172a",
            color=TEXT,
            label_style=ft.TextStyle(color="#94a3b8"),
            border_color="#334155",
            focused_border_color=ACCENT,
            expand=True,
        )

        type_dd = ft.Dropdown(
            ref=self._type_ref,
            label="Type",
            value=self._editing.habit_type if self._editing else "YES_NO",
            options=[ft.dropdown.Option(t) for t in HABIT_TYPES],
            bgcolor="#0f172a",
            color=TEXT,
            label_style=ft.TextStyle(color="#94a3b8"),
            border_color="#334155",
            focused_border_color=ACCENT,
            width=160,
        )

        icon_dd = ft.Dropdown(
            ref=self._icon_ref,
            label="Icon",
            value=self._editing.icon if self._editing else "⭐",
            options=[ft.dropdown.Option(i) for i in ICON_OPTIONS],
            bgcolor="#0f172a",
            color=TEXT,
            label_style=ft.TextStyle(color="#94a3b8"),
            border_color="#334155",
            focused_border_color=ACCENT,
            width=100,
        )

        color_dd = ft.Dropdown(
            ref=self._color_ref,
            label="Color",
            value=self._editing.color if self._editing else "#6366f1",
            options=[ft.dropdown.Option(c) for c in COLOR_OPTIONS],
            bgcolor="#0f172a",
            color=TEXT,
            label_style=ft.TextStyle(color="#94a3b8"),
            border_color="#334155",
            focused_border_color=ACCENT,
            width=130,
        )

        target_field = ft.TextField(
            ref=self._target_ref,
            label="Target",
            value=str(self._editing.target_value) if self._editing else "1",
            keyboard_type=ft.KeyboardType.NUMBER,
            bgcolor="#0f172a",
            color=TEXT,
            label_style=ft.TextStyle(color="#94a3b8"),
            border_color="#334155",
            focused_border_color=ACCENT,
            width=90,
        )

        unit_field = ft.TextField(
            ref=self._unit_ref,
            label="Unit",
            value=self._editing.unit if self._editing else "",
            bgcolor="#0f172a",
            color=TEXT,
            label_style=ft.TextStyle(color="#94a3b8"),
            border_color="#334155",
            focused_border_color=ACCENT,
            width=100,
        )

        save_btn = ft.ElevatedButton(
            text="Save" if self._editing else "Add Habit",
            bgcolor=ACCENT,
            color=TEXT,
            on_click=self._on_save,
        )

        cancel_btn = (
            ft.TextButton("Cancel", on_click=self._on_cancel, style=ft.ButtonStyle(color=DANGER))
            if self._editing
            else ft.Container()
        )

        return ft.Container(
            bgcolor=CARD,
            border_radius=8,
            padding=16,
            content=ft.Column(
                [
                    ft.Text(title, color=TEXT, size=15, weight=ft.FontWeight.BOLD),
                    ft.Row([name_field, type_dd], spacing=8),
                    ft.Row([icon_dd, color_dd, target_field, unit_field], spacing=8),
                    ft.Row([save_btn, cancel_btn], spacing=8),
                ],
                spacing=12,
            ),
        )

    def _build_habit_list(self) -> list:
        habits = habit_service.get_all_habits()
        if not habits:
            return [ft.Text("No habits yet.", color="#94a3b8", size=13)]
        return [self._habit_tile(h) for h in habits]

    def _habit_tile(self, habit: Habit) -> ft.Container:
        return ft.Container(
            bgcolor=CARD,
            border_radius=8,
            padding=ft.padding.symmetric(horizontal=16, vertical=10),
            content=ft.Row(
                [
                    ft.Text(habit.icon, size=20),
                    ft.Column(
                        [
                            ft.Text(habit.name, color=TEXT, size=14, weight=ft.FontWeight.W_500),
                            ft.Text(
                                f"{habit.habit_type} · target: {habit.target_value} {habit.unit}",
                                color="#94a3b8",
                                size=11,
                            ),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    ft.Container(
                        width=12,
                        height=12,
                        border_radius=6,
                        bgcolor=habit.color,
                    ),
                    ft.IconButton(
                        icon=ft.icons.EDIT,
                        icon_color=ACCENT,
                        icon_size=18,
                        tooltip="Edit",
                        on_click=lambda e, h=habit: self._on_edit(h),
                    ),
                    ft.IconButton(
                        icon=ft.icons.DELETE_OUTLINE,
                        icon_color=DANGER,
                        icon_size=18,
                        tooltip="Delete",
                        on_click=lambda e, h=habit: self._on_delete(h),
                    ),
                ],
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

    # ------------------------------------------------------------------
    def _on_save(self, e):
        name = self._name_ref.current.value.strip()
        if not name:
            self._show_snack("Habit name is required.", error=True)
            return
        habit_type = self._type_ref.current.value or "YES_NO"
        icon = self._icon_ref.current.value or "⭐"
        color = self._color_ref.current.value or "#6366f1"
        try:
            target = float(self._target_ref.current.value or "1")
        except ValueError:
            target = 1.0
        unit = self._unit_ref.current.value or ""

        if self._editing:
            self._editing.name = name
            self._editing.habit_type = habit_type
            self._editing.icon = icon
            self._editing.color = color
            self._editing.target_value = target
            self._editing.unit = unit
            habit_service.update_habit(self._editing)
            self._editing = None
            self._show_snack("Habit updated!")
        else:
            habit_service.create_habit(name, habit_type, color, icon, target, unit)
            self._show_snack("Habit added!")

        self._rebuild()

    def _on_cancel(self, e):
        self._editing = None
        self._rebuild()

    def _on_edit(self, habit: Habit):
        self._editing = habit
        self._rebuild()

    def _on_delete(self, habit: Habit):
        def confirm_delete(e):
            habit_service.delete_habit(habit.id)
            dialog.open = False
            self.page.update()
            self._rebuild()
            self._show_snack(f"'{habit.name}' deleted.")

        def cancel(e):
            dialog.open = False
            self.page.update()

        dialog = ft.AlertDialog(
            title=ft.Text(f"Delete '{habit.name}'?", color=TEXT),
            content=ft.Text("This action cannot be undone.", color="#94a3b8"),
            bgcolor=CARD,
            actions=[
                ft.TextButton("Cancel", on_click=cancel),
                ft.ElevatedButton("Delete", bgcolor=DANGER, color=TEXT, on_click=confirm_delete),
            ],
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    # ------------------------------------------------------------------
    def _rebuild(self):
        """Refresh form and list in-place."""
        self.update()

    def _show_snack(self, msg: str, error: bool = False):
        snack = ft.SnackBar(
            content=ft.Text(msg, color=TEXT),
            bgcolor=DANGER if error else SUCCESS,
        )
        self.page.snack_bar = snack
        snack.open = True
        self.page.update()
