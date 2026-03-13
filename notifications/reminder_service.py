"""Background reminder service using Python threading."""
import threading
import time
from datetime import datetime
from config import load_config

REMINDER_COOLDOWN_SECONDS = 60  # sleep one full minute to avoid re-triggering in the same HH:MM window
POLL_INTERVAL_SECONDS = 30


class ReminderService:
    """Fires a callback at the configured reminder time each day."""

    def __init__(self):
        self._thread = None
        self._running = False
        self._callback = None

    def start(self, callback=None) -> None:
        """Start the reminder background thread."""
        self._callback = callback
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop the reminder background thread."""
        self._running = False

    def _run(self) -> None:
        while self._running:
            config = load_config()
            reminder_time = config.get("reminder_time", "09:00")
            now = datetime.now().strftime("%H:%M")
            if now == reminder_time:
                if self._callback:
                    try:
                        self._callback()
                    except Exception:
                        pass
                time.sleep(REMINDER_COOLDOWN_SECONDS)
            time.sleep(POLL_INTERVAL_SECONDS)
