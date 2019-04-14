"""
Date management
"""

from datetime import datetime

from typing import Sequence

from arrow import arrow


def relevant_days_between(start_date: datetime, end_date: datetime) -> Sequence[datetime]:
    """
    Get the list of dates representing the weekdays between (including) two dates

    :param start_date: Starting date
    :param end_date: Ending date
    :return: The list of dates
    """
    WEEKDAY_SATURDAY = 5
    return [d.datetime for d in arrow.Arrow.range('day', start_date, end_date) if d.weekday() < WEEKDAY_SATURDAY]


def jira_date(d: datetime) -> str:
    """
    Transforms a datetime into a string representing a date in a JQL query

    :param d: The date
    :return: A string
    """
    return arrow.Arrow.fromdatetime(d).strftime('%Y/%m/%d')
