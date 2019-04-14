"""
Tests for dates.jira_date
"""
import arrow
import pytest
from hamcrest import assert_that, equal_to

import dates


@pytest.mark.parametrize('date, jira_date', [
    (arrow.Arrow(2019, 1, 2).datetime, '2019/01/02'),
])
def test_jira_date(date, jira_date):
    assert_that(dates.jira_date(date), equal_to(jira_date))
