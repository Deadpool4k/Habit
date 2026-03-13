"""Single habit row used inside the habit grid."""
import calendar
import flet as ft

BG = "#0f172a"
CARD = "#1e293b"
ACCENT = "#6366f1"
SUCCESS = "#22c55e"
TEXT = "#f1f5f9"
DANGER = "#ef4444"

CELL_W = 28
CELL_H = 28


class HabitRow(ft.Row):
    """One row in the habit grid: name + icon + streak + day-cells."""

    def __init__(
        self,
        habit,
        year: int,
        month: int,
        completed_dates: list[str],
        on_toggle,
        streak: int = 0,
    ):
        super().__init__(
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        self.habit = habit
        self.year = year
        self.month = month
        self.completed_dates = set(completed_dates)
        self.on_toggle = on_toggle
        self.streak = streak

        days_in_month = calendar.monthrange(year, month)[1]

        def make_cell(day: int):
            date_str = f"{year:04d}-{month:02d}-{day:02d}"
            done = date_str in self.completed_dates
            color = SUCCESS if done else CARD

            def on_click(e, ds=date_str):
                self.on_toggle(habit.id, ds)

            return ft.Container(
                width=CELL_W,
                height=CELL_H,
                border_radius=4,
                bgcolor=color,
                border=ft.border.all(1, "#334155"),
                on_click=on_click,
                tooltip=date_str,
            )

        cells = [make_cell(d) for d in range(1, days_in_month + 1)]

        name_col = ft.Container(
            width=160,
            content=ft.Row(
                [
                    ft.Text(habit.icon, size=16),
                    ft.Text(
                        habit.name,
                        color=TEXT,
                        size=13,
                        overflow=ft.TextOverflow.ELLIPSIS,
                        max_lines=1,
                        expand=True,
                    ),
                    ft.Text(
                        f"🔥{streak}",
                        size=11,
                        color="#fb923c",
                    ),
                ],
                spacing=4,
                tight=True,
            ),
        )

        self.controls = [
            name_col,
            ft.Row(cells, spacing=2, scroll=ft.ScrollMode.AUTO),
        ]
