"""Circular progress indicator component."""
import math
import flet as ft

TEXT = "#f1f5f9"
ACCENT = "#6366f1"
CARD = "#1e293b"


class ProgressCircle(ft.UserControl):
    """Shows completed/total as a ProgressRing with a label inside."""

    def __init__(self, completed: int, total: int, size: float = 100):
        super().__init__()
        self.completed = completed
        self.total = total
        self.size = size

    def build(self):
        ratio = (self.completed / self.total) if self.total > 0 else 0.0

        ring = ft.ProgressRing(
            value=ratio,
            width=self.size,
            height=self.size,
            stroke_width=10,
            color=ACCENT,
            bgcolor="#334155",
        )

        label = ft.Text(
            f"{self.completed}/{self.total}",
            color=TEXT,
            size=16,
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER,
        )

        sub = ft.Text(
            "Today",
            color="#94a3b8",
            size=11,
            text_align=ft.TextAlign.CENTER,
        )

        return ft.Stack(
            [
                ring,
                ft.Container(
                    width=self.size,
                    height=self.size,
                    content=ft.Column(
                        [label, sub],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=0,
                    ),
                    alignment=ft.alignment.center,
                ),
            ],
            width=self.size,
            height=self.size,
        )
