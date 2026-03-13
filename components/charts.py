"""Chart components — custom bar and line charts using Flet layout controls."""
import flet as ft

ACCENT = "#6366f1"
SUCCESS = "#22c55e"
TEXT = "#f1f5f9"
CARD = "#1e293b"
MUTED = "#94a3b8"
GRID = "#334155"

CHART_HEIGHT = 160
BAR_WIDTH = 24
DOT_R = 5


def build_bar_chart(data: list[dict]) -> ft.Control:
    """Build a bar chart from a list of {date, completed, total} dicts."""
    if not data:
        data = [{"date": "N/A", "completed": 0, "total": 1}]

    max_val = max((d.get("total", 1) for d in data), default=1) or 1

    bars = []
    for item in data:
        completed = item.get("completed", 0)
        total = item.get("total", 1) or 1
        ratio = completed / max_val
        bar_h = max(2, int(ratio * CHART_HEIGHT))
        label = item.get("date", "")[-5:]  # MM-DD

        bars.append(
            ft.Column(
                [
                    ft.Text(str(completed), size=9, color=MUTED, text_align=ft.TextAlign.CENTER),
                    ft.Container(
                        width=BAR_WIDTH,
                        height=CHART_HEIGHT - bar_h,
                    ),
                    ft.Container(
                        width=BAR_WIDTH,
                        height=bar_h,
                        bgcolor=ACCENT,
                        border_radius=ft.border_radius.only(top_left=3, top_right=3),
                        tooltip=f"{label}: {completed}/{total}",
                    ),
                    ft.Text(label, size=8, color=MUTED, text_align=ft.TextAlign.CENTER, width=BAR_WIDTH),
                ],
                spacing=0,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        )

    return ft.Container(
        height=CHART_HEIGHT + 36,
        content=ft.Row(
            bars,
            spacing=6,
            vertical_alignment=ft.CrossAxisAlignment.END,
        ),
    )


def build_line_chart(data: list[dict]) -> ft.Control:
    """Build a line chart from a list of {date, completed, total} dicts."""
    if not data:
        data = [{"date": "N/A", "completed": 0, "total": 1}]

    max_val = max((d.get("total", 1) for d in data), default=1) or 1
    # Show every Nth label to avoid crowding
    step = max(1, len(data) // 10)

    rows_list = []
    for i, item in enumerate(data):
        completed = item.get("completed", 0)
        total = item.get("total", 1) or 1
        ratio = completed / max_val if max_val else 0
        bar_w = max(2, int(ratio * 180))
        label = item.get("date", "")[-5:] if i % step == 0 else ""

        rows_list.append(
            ft.Row(
                [
                    ft.Text(label, size=8, color=MUTED, width=40, text_align=ft.TextAlign.RIGHT),
                    ft.Container(
                        width=bar_w,
                        height=6,
                        bgcolor=SUCCESS,
                        border_radius=3,
                        tooltip=f"{item.get('date','')} {completed}/{total}",
                    ),
                    ft.Text(str(completed), size=8, color=MUTED),
                ],
                spacing=6,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            )
        )

    return ft.Container(
        content=ft.Column(rows_list, spacing=3, scroll=ft.ScrollMode.AUTO),
        height=CHART_HEIGHT + 20,
    )
