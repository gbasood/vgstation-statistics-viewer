"""Helper functions for Jinja2 templates."""
import calendar
import datetime


def add_months(sourcedate, months):
    """Add months to original date. Returns a datetime."""
    month = sourcedate.month - 1 + months
    year = int(sourcedate.year + month / 12)
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year, month)[1])
    return datetime.date(year, month, day)
