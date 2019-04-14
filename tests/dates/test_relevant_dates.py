"""
Tests for dates.relevant_days_between
"""

import arrow
from hamcrest import assert_that, has_length, contains

import dates


def test_includes_start_and_end():
    start = arrow.Arrow(2019, 1, 2)
    end = arrow.Arrow(2019, 1, 3)
    res = dates.relevant_days_between(start.datetime, end.datetime)
    assert_that(list(res), has_length(2))
    assert_that(res, contains(start, end))


def test_includes_weekdays_between_start_and_end():
    start = arrow.Arrow(2019, 1, 2)
    end = arrow.Arrow(2019, 1, 4)
    res = dates.relevant_days_between(start.datetime, end.datetime)
    assert_that(list(res), has_length(3))
    assert_that(res, contains(start, arrow.Arrow(2019, 1, 3).datetime, end))


def test_does_not_include_non_weekdays_between_start_and_end():
    start = arrow.Arrow(2019, 1, 4)
    end = arrow.Arrow(2019, 1, 8)
    res = dates.relevant_days_between(start.datetime, end.datetime)
    assert_that(list(res), has_length(3))
    assert_that(res, contains(start, arrow.Arrow(2019, 1, 7).datetime, end))
