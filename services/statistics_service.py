"""Business logic for statistics and analytics."""
import repositories.stats_repository as repo


def get_weekly_stats() -> list[dict]:
    """Return per-day completion stats for the last 7 days."""
    return repo.get_weekly_completion()


def get_monthly_stats(year: int, month: int) -> list[dict]:
    """Return per-day completion stats for the given calendar month."""
    return repo.get_monthly_completion(year, month)


def get_heatmap_data(year: int, month: int) -> dict[str, int]:
    """Return a date → completion_count mapping for the heatmap."""
    return repo.get_activity_heatmap(year, month)
