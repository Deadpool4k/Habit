"""Circular progress indicator component."""
import flet as ft

TEXT = "#f1f5f9"
ACCENT = "#6366f1"
CARD = "#1e293b"


class ProgressCircle(ft.Stack):
    """Shows completed/total as a ProgressRing with a label inside."""

    def __init__(self, completed: int, total: int, size: float = 100):
        super().__init__()
        self.completed = completed
        self.total = total
        self.size = size
        self.width = size
        self.height = size

        ratio = (completed / total) if total > 0 else 0.0

        ring = ft.ProgressRing(
            value=ratio,
            width=size,
            height=size,
            stroke_width=10,
            color=ACCENT,
            bgcolor="#334155",
        )

        label = ft.Text(
            f"{completed}/{total}",
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

        self.controls = [
            ring,
            ft.Container(
                width=size,
                height=size,
                content=ft.Column(
                    [label, sub],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=0,
                ),
                alignment=ft.alignment.Alignment(0, 0),
            ),
        ]
