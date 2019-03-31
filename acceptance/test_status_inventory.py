import subprocess
import json
import pytest
from hamcrest import assert_that, equal_to
from mbtest.server import MountebankServer
from mbtest.imposters import Imposter

from matchers.output import (
    has_header_with_columns_in_lexicographical_order,
    has_header_with_columns_in_the_same_order,
    completed_successfully,
    output_cell_has_value
)


@pytest.fixture
def issues_6_in_sprint(datadir, mock_jira) -> Imposter:
    with open(datadir / 'jira.json', 'r') as f:
        return Imposter.from_structure(json.load(f))


def test_shows_status_inventory(mock_jira: MountebankServer, issues_6_in_sprint: Imposter):
    query: str = 'project=SCRUM1 and sprint in openSprints()'
    with mock_jira(issues_6_in_sprint):
        result: subprocess.CompletedProcess = subprocess.run(
            ['python', 'team2.py', 'columns', '--url', str(issues_6_in_sprint.url), query],
            stdout=subprocess.PIPE
        )
        assert_that(result, completed_successfully())
        assert_that(result, has_header_with_columns_in_lexicographical_order(['Done', 'In Progress', 'To Do']))
        assert_that(result, output_cell_has_value(0, 'Done', 3))
        assert_that(result, output_cell_has_value(0, 'In Progress', 2))
        assert_that(result, output_cell_has_value(0, 'To Do', 1))


def test_shows_status_inventory_in_order(mock_jira: MountebankServer, issues_6_in_sprint: Imposter):
    query: str = 'project=SCRUM1 and sprint in openSprints()'
    with mock_jira(issues_6_in_sprint):
        result: subprocess.CompletedProcess = subprocess.run(
            ['python', 'team2.py', 'columns', '--col-names', 'To Do:In Progress:Done', '--url',
             str(issues_6_in_sprint.url), query],
            stdout=subprocess.PIPE
        )
        assert_that(result, completed_successfully())
        assert_that(result, has_header_with_columns_in_the_same_order(['To Do', 'In Progress', 'Done']))
        assert_that(result, output_cell_has_value(0, 'To Do', 1))
        assert_that(result, output_cell_has_value(0, 'In Progress', 2))
        assert_that(result, output_cell_has_value(0, 'Done', 3))


def test_shows_status_inventory_with_not_found_statuses(mock_jira: MountebankServer, issues_6_in_sprint: Imposter):
    query: str = 'project=SCRUM1 and sprint in openSprints()'
    with mock_jira(issues_6_in_sprint):
        result: subprocess.CompletedProcess = subprocess.run(
            ['python', 'team2.py', 'columns', '--col-names', 'To Do:In Progress:Blocked:Done', '--url',
             str(issues_6_in_sprint.url), query],
            stdout=subprocess.PIPE
        )
        assert_that(result, completed_successfully())
        assert_that(result, has_header_with_columns_in_the_same_order(['To Do', 'In Progress', 'Blocked', 'Done']))
        assert_that(result, output_cell_has_value(0, 'To Do', 1))
        assert_that(result, output_cell_has_value(0, 'In Progress', 2))
        assert_that(result, output_cell_has_value(0, 'Blocked', 0))
        assert_that(result, output_cell_has_value(0, 'Done', 3))


def test_shows_status_inventory_maps_status_name(mock_jira: MountebankServer, issues_6_in_sprint: Imposter):
    query: str = 'project=SCRUM1 and sprint in openSprints()'
    with mock_jira(issues_6_in_sprint):
        result: subprocess.CompletedProcess = subprocess.run(
            ['python', 'team2.py', 'columns',
             '--url', str(issues_6_in_sprint.url),
             '--map', 'To Do:TODO',
             query],
            stdout=subprocess.PIPE
        )
        assert_that(result, completed_successfully())
        assert_that(result, has_header_with_columns_in_lexicographical_order(['TODO', 'In Progress', 'Done']))
        assert_that(result, output_cell_has_value(0, 'TODO', 1))
        assert_that(result, output_cell_has_value(0, 'In Progress', 2))
        assert_that(result, output_cell_has_value(0, 'Done', 3))


def test_shows_status_inventory_maps_multiple_status_names(mock_jira: MountebankServer, issues_6_in_sprint: Imposter):
    query: str = 'project=SCRUM1 and sprint in openSprints()'
    with mock_jira(issues_6_in_sprint):
        result: subprocess.CompletedProcess = subprocess.run(
            ['python', 'team2.py', 'columns',
             '--url', str(issues_6_in_sprint.url),
             '--map', 'To Do:TODO',
             '--map', 'Done:DONE',
             query],
            stdout=subprocess.PIPE
        )
        assert_that(result, completed_successfully())
        assert_that(result, has_header_with_columns_in_lexicographical_order(['In Progress', 'TODO', 'DONE']))
        lines: [str] = result.stdout.decode('utf-8').split('\n')
        assert_that(lines[0], equal_to('DONE,In Progress,TODO'))
        assert_that(lines[1], equal_to('3,2,1'))
        assert_that(result, output_cell_has_value(0, 'TODO', 1))
        assert_that(result, output_cell_has_value(0, 'In Progress', 2))
        assert_that(result, output_cell_has_value(0, 'DONE', 3))
