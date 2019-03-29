import subprocess
import json
import pytest
from hamcrest import assert_that, equal_to
from mbtest.server import MountebankServer
from mbtest.imposters import Imposter


@pytest.fixture
def issues_6_in_sprint(datadir, mock_jira) -> Imposter:
    with open(datadir / 'jira.json', 'r') as f:
        return Imposter.from_structure(json.load(f))


def test_shows_column_inventory(mock_jira: MountebankServer, issues_6_in_sprint: Imposter):
    query: str = 'project=SCRUM1 and sprint in openSprints()'
    with mock_jira(issues_6_in_sprint):
        result: subprocess.CompletedProcess = subprocess.run(
            ['python', 'team2.py', 'columns', '--url', str(issues_6_in_sprint.url), query],
            stdout=subprocess.PIPE
        )
        assert_that(result.returncode, equal_to(0))
        lines: [str] = result.stdout.decode('utf-8').split('\n')
        assert_that(lines[0], equal_to('Done,In Progress,To Do'))
        assert_that(lines[1], equal_to('3,2,1'))


def test_shows_column_inventory_in_order(mock_jira: MountebankServer, issues_6_in_sprint: Imposter):
    query: str = 'project=SCRUM1 and sprint in openSprints()'
    with mock_jira(issues_6_in_sprint):
        result: subprocess.CompletedProcess = subprocess.run(
            ['python', 'team2.py', 'columns', '--col-names', 'To Do:In Progress:Done', '--url',
             str(issues_6_in_sprint.url), query],
            stdout=subprocess.PIPE
        )
        assert_that(result.returncode, equal_to(0))
        lines: [str] = result.stdout.decode('utf-8').split('\n')
        assert_that(lines[0], equal_to('To Do,In Progress,Done'))
        assert_that(lines[1], equal_to('1,2,3'))


def test_shows_column_inventory_maps_status_name(mock_jira: MountebankServer, issues_6_in_sprint: Imposter):
    query: str = 'project=SCRUM1 and sprint in openSprints()'
    with mock_jira(issues_6_in_sprint):
        result: subprocess.CompletedProcess = subprocess.run(
            ['python', 'team2.py', 'columns',
             '--url', str(issues_6_in_sprint.url),
             '--map', 'To Do:TODO',
             query],
            stdout=subprocess.PIPE
        )
        assert_that(result.returncode, equal_to(0))
        lines: [str] = result.stdout.decode('utf-8').split('\n')
        assert_that(lines[0], equal_to('Done,In Progress,TODO'))
        assert_that(lines[1], equal_to('3,2,1'))


def test_shows_column_inventory_maps_multiple_status_names(mock_jira: MountebankServer, issues_6_in_sprint: Imposter):
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
        assert_that(result.returncode, equal_to(0))
        lines: [str] = result.stdout.decode('utf-8').split('\n')
        assert_that(lines[0], equal_to('DONE,In Progress,TODO'))
        assert_that(lines[1], equal_to('3,2,1'))
