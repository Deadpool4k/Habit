"""Habits page — monthly grid, streaks, progress, charts and heatmap."""
import calendar
from datetime import date

import flet as ft

from services import habit_service, statistics_service
from components.habit_row import HabitRow
from components.progress_circle import ProgressCircle
from components.calendar_grid import CalendarGrid
from components.charts import build_bar_chart, build_line_chart

BG = "#0f172a"
CARD = "#1e293b"
ACCENT = "#6366f1"
SUCCESS = "#22c55e"
TEXT = "#f1f5f9"
DANGER = "#ef4444"

MONTH_NAMES = [
    "", "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]


class HabitsPage(ft.Column):
    """Main habits tracking page with calendar grid and statistics."""

    def __init__(self, flet_page: ft.Page):
        super().__init__(expand=True, spacing=0)
        self._page = flet_page
        today = date.today()
        self.current_year = today.year
        self.current_month = today.month
        self._month_label_ref = ft.Ref[ft.Text]()

        self._body = ft.Column(
            controls=[
                self._build_grid_section(),
                self._build_progress_row(),
                self._build_stats_section(),
            ],
            scroll=ft.ScrollMode.AUTO,
            spacing=16,
            expand=True,
        )

        self.controls = [
            self._build_header(),
            ft.Container(
                expand=True,
                content=self._body,
                padding=16,
            ),
        ]

    # ------------------------------------------------------------------
    def _build_header(self):
        return ft.Container(
            bgcolor=CARD,
            padding=ft.padding.symmetric(horizontal=20, vertical=12),
            content=ft.Row(
                [
                    ft.Text("📅 Habits", color=TEXT, size=20, weight=ft.FontWeight.BOLD),
                    ft.Row(
                        [
                            ft.IconButton(
                                icon=ft.Icons.CHEVRON_LEFT,
                                icon_color=TEXT,
                                on_click=self._prev_month,
                            ),
                            ft.Text(
                                ref=self._month_label_ref,
                                value=f"{MONTH_NAMES[self.current_month]} {self.current_year}",
                                color=TEXT,
                                size=16,
                                weight=ft.FontWeight.W_600,
                                width=160,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.CHEVRON_RIGHT,
                                icon_color=TEXT,
                                on_click=self._next_month,
                            ),
                        ],
                        spacing=0,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
        )

    def _build_grid_section(self):
        habits = habit_service.get_all_habits()
        entries = habit_service.get_habits_for_month(self.current_year, self.current_month)
        days_in_month = calendar.monthrange(self.current_year, self.current_month)[1]

        # Day number header row
        header_cells = [
            ft.Container(
                width=28,
                height=20,
                content=ft.Text(
                    str(d), size=9, color="#94a3b8", text_align=ft.TextAlign.CENTER
                ),
                alignment=ft.alignment.Alignment(0, 0),
            )
            for d in range(1, days_in_month + 1)
        ]
        header = ft.Row(
            [
                ft.Container(width=160),
                ft.Row(header_cells, spacing=2, scroll=ft.ScrollMode.AUTO),
            ],
            spacing=8,
        )

        if not habits:
            rows = [ft.Text("No habits yet. Go to Edit Habits to add some!", color="#94a3b8", size=14)]
        else:
            rows = [
                HabitRow(
                    habit=h,
                    year=self.current_year,
                    month=self.current_month,
                    completed_dates=entries.get(h.id, []),
                    on_toggle=self._on_toggle,
                    streak=habit_service.calculate_streak(h.id),
                )
                for h in habits
            ]

        return ft.Container(
            bgcolor=CARD,
            border_radius=8,
            padding=12,
            content=ft.Column(
                controls=[
                    ft.Text("Habit Grid", color=TEXT, size=14, weight=ft.FontWeight.BOLD),
                    header,
                    ft.Divider(color="#334155", height=1),
                    *rows,
                ],
                spacing=6,
            ),
        )

    def _build_progress_row(self):
        completed, total = habit_service.get_today_progress()
        circle = ProgressCircle(completed, total)
        return ft.Container(
            bgcolor=CARD,
            border_radius=8,
            padding=16,
            content=ft.Row(
                [
                    circle,
                    ft.Column(
                        [
                            ft.Text("Today's Progress", color=TEXT, size=14, weight=ft.FontWeight.BOLD),
                            ft.Text(
                                f"{completed} of {total} habits completed",
                                color="#94a3b8",
                                size=13,
                            ),
                        ],
                        spacing=4,
                    ),
                ],
                spacing=20,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

    def _build_stats_section(self):
        weekly = statistics_service.get_weekly_stats()
        monthly = statistics_service.get_monthly_stats(self.current_year, self.current_month)
        heatmap = statistics_service.get_heatmap_data(self.current_year, self.current_month)

        bar = build_bar_chart(weekly)
        line = build_line_chart(monthly)
        heat = CalendarGrid(self.current_year, self.current_month, heatmap)

        return ft.Column(
            controls=[
                ft.Container(
                    bgcolor=CARD,
                    border_radius=8,
                    padding=12,
                    content=ft.Column(
                        [
                            ft.Text("Weekly Completion (last 7 days)", color=TEXT, size=14, weight=ft.FontWeight.BOLD),
                            bar,
                        ],
                        spacing=8,
                    ),
                ),
                ft.Container(
                    bgcolor=CARD,
                    border_radius=8,
                    padding=12,
                    content=ft.Column(
                        [
                            ft.Text(
                                f"Monthly Progress — {MONTH_NAMES[self.current_month]} {self.current_year}",
                                color=TEXT,
                                size=14,
                                weight=ft.FontWeight.BOLD,
                            ),
                            line,
                        ],
                        spacing=8,
                    ),
                ),
                heat,
            ],
            spacing=16,
        )

    # ------------------------------------------------------------------
    def _on_toggle(self, habit_id: int, date_str: str):
        habit_service.toggle_habit(habit_id, date_str)
        self._refresh()

    def _prev_month(self, e):
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self._refresh()

    def _next_month(self, e):
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self._refresh()

    def _refresh(self):
        """Re-render the body sections after state changes."""
        if self._month_label_ref.current:
            self._month_label_ref.current.value = (
                f"{MONTH_NAMES[self.current_month]} {self.current_year}"
            )
            self._month_label_ref.current.update()
        self._body.controls = [
            self._build_grid_section(),
            self._build_progress_row(),
            self._build_stats_section(),
        ]
        self._body.update()
