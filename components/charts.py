"""Chart components using Flet's built-in BarChart and LineChart."""
import flet as ft

ACCENT = "#6366f1"
SUCCESS = "#22c55e"
TEXT = "#f1f5f9"
CARD = "#1e293b"


def build_bar_chart(data: list[dict]) -> ft.BarChart:
    """Build a bar chart from a list of {date, completed, total} dicts."""
    if not data:
        data = [{"date": "N/A", "completed": 0, "total": 1}]

    max_val = max((d.get("total", 1) for d in data), default=1) or 1

    groups = []
    for i, item in enumerate(data):
        completed = item.get("completed", 0)
        total = item.get("total", 1) or 1
        label = item.get("date", "")[-5:]  # MM-DD

        groups.append(
            ft.BarChartGroup(
                x=i,
                bar_rods=[
                    ft.BarChartRod(
                        from_y=0,
                        to_y=completed,
                        width=18,
                        color=ACCENT,
                        tooltip=f"{label}\n{completed}/{total}",
                        border_radius=ft.border_radius.only(
                            top_left=4, top_right=4
                        ),
                    ),
                ],
            )
        )

    bottom_labels = ft.ChartAxis(
        labels=[
            ft.ChartAxisLabel(
                value=i,
                label=ft.Text(
                    item.get("date", "")[-5:],
                    size=9,
                    color="#94a3b8",
                    no_wrap=True,
                ),
            )
            for i, item in enumerate(data)
        ],
        labels_size=28,
    )

    left_axis = ft.ChartAxis(
        labels_size=32,
        labels=[
            ft.ChartAxisLabel(
                value=v,
                label=ft.Text(str(v), size=9, color="#94a3b8"),
            )
            for v in range(0, max_val + 1)
        ],
    )

    return ft.BarChart(
        bar_groups=groups,
        bgcolor=CARD,
        border=ft.border.all(1, "#334155"),
        left_axis=left_axis,
        bottom_axis=bottom_labels,
        horizontal_grid_lines=ft.ChartGridLines(interval=1, color="#334155", width=0.5),
        interactive=True,
        expand=True,
        max_y=max_val + 0.5,
        height=180,
    )


def build_line_chart(data: list[dict]) -> ft.LineChart:
    """Build a line chart from a list of {date, completed, total} dicts."""
    if not data:
        data = [{"date": "N/A", "completed": 0, "total": 1}]

    max_val = max((d.get("total", 1) for d in data), default=1) or 1

    data_points = [
        ft.LineChartDataPoint(
            x=i,
            y=item.get("completed", 0),
            tooltip=f"{item.get('date','')[-5:]}: {item.get('completed',0)}/{item.get('total',1)}",
        )
        for i, item in enumerate(data)
    ]

    series = ft.LineChartData(
        data_points=data_points,
        color=SUCCESS,
        stroke_width=2,
        curved=True,
        stroke_cap_round=True,
        below_line_bgcolor=ft.colors.with_opacity(0.1, SUCCESS),
    )

    bottom_labels = ft.ChartAxis(
        labels=[
            ft.ChartAxisLabel(
                value=i,
                label=ft.Text(
                    item.get("date", "")[-5:],
                    size=9,
                    color="#94a3b8",
                    no_wrap=True,
                ),
            )
            for i, item in enumerate(data)
            if i % max(1, len(data) // 7) == 0
        ],
        labels_size=28,
    )

    return ft.LineChart(
        data_series=[series],
        bgcolor=CARD,
        border=ft.border.all(1, "#334155"),
        left_axis=ft.ChartAxis(labels_size=32),
        bottom_axis=bottom_labels,
        horizontal_grid_lines=ft.ChartGridLines(interval=1, color="#334155", width=0.5),
        interactive=True,
        expand=True,
        min_y=0,
        max_y=max_val + 0.5,
        height=180,
    )
