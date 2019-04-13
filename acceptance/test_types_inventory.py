import json
import subprocess

import pytest
from hamcrest import assert_that
from mbtest.imposters import Imposter
from mbtest.server import MountebankServer

from testing.matchers import (
    has_header_with_columns_in_lexicographical_order,
    has_header_with_columns_in_the_same_order,
    completed_successfully,
    output_cell_has_value
)

from testing.runner import command


@pytest.fixture
def issues_3_in_sprint(datadir, mock_jira) -> Imposter:
    with open(datadir / 'jira.json', 'r') as f:
        return Imposter.from_structure(json.load(f))


def test_shows_types_inventory(mock_jira: MountebankServer, issues_3_in_sprint: Imposter):
    query: str = 'project=SCRUM2 and sprint in openSprints()'
    with mock_jira(issues_3_in_sprint):
        result: subprocess.CompletedProcess = command(). \
            with_global_option('--url', str(issues_3_in_sprint.url)). \
            with_subcommand('types'). \
            with_argument(query). \
            run()
        assert_that(result, completed_successfully())
        assert_that(result, has_header_with_columns_in_lexicographical_order(['Bug', 'Story']))
        assert_that(result, output_cell_has_value(0, 'Bug', 1))
        assert_that(result, output_cell_has_value(0, 'Story', 2))


def test_shows_types_inventory_in_order(mock_jira: MountebankServer, issues_3_in_sprint: Imposter):
    query: str = 'project=SCRUM2 and sprint in openSprints()'
    with mock_jira(issues_3_in_sprint):
        result: subprocess.CompletedProcess = command(). \
            with_global_option('--url', str(issues_3_in_sprint.url)). \
            with_subcommand('types'). \
            with_option('--col-names', 'Story:Bug'). \
            with_argument(query). \
            run()
        assert_that(result, completed_successfully())
        assert_that(result, has_header_with_columns_in_the_same_order(['Story', 'Bug']))
        assert_that(result, output_cell_has_value(0, 'Bug', 1))
        assert_that(result, output_cell_has_value(0, 'Story', 2))


def test_shows_types_inventory_with_unknown_types(mock_jira: MountebankServer, issues_3_in_sprint: Imposter):
    query: str = 'project=SCRUM2 and sprint in openSprints()'
    with mock_jira(issues_3_in_sprint):
        result: subprocess.CompletedProcess = command(). \
            with_global_option('--url', str(issues_3_in_sprint.url)). \
            with_subcommand('types'). \
            with_option('--col-names', 'Story:Bug:Task'). \
            with_argument(query). \
            run()
        assert_that(result, completed_successfully())
        assert_that(result, has_header_with_columns_in_the_same_order(['Story', 'Bug', 'Task']))
        assert_that(result, output_cell_has_value(0, 'Bug', 1))
        assert_that(result, output_cell_has_value(0, 'Story', 2))
        assert_that(result, output_cell_has_value(0, 'Task', 0))
