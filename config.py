"""Configuration module for AI Habit & Mood Tracker."""
import json
import os

CONFIG_FILE = "config.json"
DEFAULT_CONFIG = {
    "openai_api_key": "",
    "openai_model": "gpt-4o",
    "db_path": "habit_tracker.db",
    "reminder_time": "09:00"
}


def load_config() -> dict:
    """Load configuration from file, merging with defaults."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            data = json.load(f)
        for k, v in DEFAULT_CONFIG.items():
            if k not in data:
                data[k] = v
        return data
    return DEFAULT_CONFIG.copy()


def save_config(config: dict) -> None:
    """Persist configuration to disk."""
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)
