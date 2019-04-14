import json

import pytest
from hamcrest import assert_that
from mbtest.imposters import Imposter
from mbtest.server import MountebankServer

from testing.matchers import completed_successfully, output_cell_has_value, has_header_with_columns_in_the_same_order
from testing.runner import command


@pytest.fixture
def sprint_with_0_issues(datadir):
    with open(datadir / '20190109-20190122-0-issues.json', 'r') as f:
        return Imposter.from_structure(json.load(f))


def test_sprint_with_no_issues_shows_nan(mock_jira: MountebankServer, sprint_with_0_issues: Imposter):
    with mock_jira(sprint_with_0_issues):
        result = command(). \
            with_global_option('--url', str(sprint_with_0_issues.url)). \
            with_subcommand('flow-time'). \
            with_option('--project', 'SCRUM3'). \
            with_option('--start-date', '2019/01/09'). \
            with_option('--end-date', '2019/01/21'). \
            with_option('--inventory-statuses', 'In Progress'). \
            with_option('--done-statuses', 'Done'). \
            run()
        assert_that(result, completed_successfully())
        assert_that(result, has_header_with_columns_in_the_same_order(['Flow time']))
        assert_that(result, output_cell_has_value(0, 'Flow time', float('nan')))
