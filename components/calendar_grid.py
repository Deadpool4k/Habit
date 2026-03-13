"""Calendar heatmap grid component."""
import calendar
import flet as ft

CARD = "#1e293b"
TEXT = "#f1f5f9"
ACCENT = "#6366f1"


def _heat_color(count: int, max_count: int) -> str:
    """Map a completion count to a shade of indigo."""
    if max_count == 0 or count == 0:
        return "#1e293b"
    ratio = min(count / max_count, 1.0)
    if ratio < 0.25:
        return "#312e81"
    if ratio < 0.5:
        return "#4338ca"
    if ratio < 0.75:
        return "#6366f1"
    return "#818cf8"


class CalendarGrid(ft.Container):
    """Monthly heatmap calendar showing habit completion intensity."""

    def __init__(self, year: int, month: int, heatmap_data: dict[str, int]):
        super().__init__(
            bgcolor=CARD,
            border_radius=8,
            padding=12,
        )
        self.year = year
        self.month = month
        self.heatmap_data = heatmap_data

        max_count = max(heatmap_data.values(), default=1)
        days_in_month = calendar.monthrange(year, month)[1]
        first_weekday = calendar.monthrange(year, month)[0]  # 0=Mon

        day_labels = [
            ft.Container(
                width=32,
                height=24,
                content=ft.Text(d, size=10, color="#64748b", text_align=ft.TextAlign.CENTER),
                alignment=ft.alignment.Alignment(0, 0),
            )
            for d in ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
        ]

        cells: list = []
        # Empty cells before the first day
        for _ in range(first_weekday):
            cells.append(ft.Container(width=32, height=32))

        for day in range(1, days_in_month + 1):
            date_str = f"{year:04d}-{month:02d}-{day:02d}"
            count = heatmap_data.get(date_str, 0)
            color = _heat_color(count, max_count)
            cells.append(
                ft.Container(
                    width=32,
                    height=32,
                    border_radius=4,
                    bgcolor=color,
                    tooltip=f"{date_str}: {count} habits",
                    content=ft.Text(
                        str(day),
                        size=10,
                        color=TEXT,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    alignment=ft.alignment.Alignment(0, 0),
                )
            )

        # Build weeks
        rows = [ft.Row(day_labels, spacing=2)]
        for i in range(0, len(cells), 7):
            week = cells[i: i + 7]
            # Pad last row
            while len(week) < 7:
                week.append(ft.Container(width=32, height=32))
            rows.append(ft.Row(week, spacing=2))

        self.content = ft.Column(
            [
                ft.Text("Activity Heatmap", color=TEXT, size=14, weight=ft.FontWeight.BOLD),
                ft.Column(rows, spacing=2),
            ],
            spacing=8,
        )
