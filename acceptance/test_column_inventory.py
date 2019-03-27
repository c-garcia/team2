import subprocess
import json
import pytest
import requests
from hamcrest import assert_that, equal_to
from mbtest.server import MountebankServer
from mbtest.imposters import Imposter


@pytest.fixture
def issues_6_in_sprint(datadir, mock_jira) -> Imposter:
    with open(datadir / 'jira.json', 'r') as f:
        return Imposter.from_structure(json.load(f))


@pytest.mark.skip(reason="wip")
def test_shows_column_inventory(mock_jira: MountebankServer, issues_6_in_sprint: Imposter):
    query: str = 'project = SCRUM1 and sprint in openSprints()'
    with mock_jira(issues_6_in_sprint) as jira_server:
        result: subprocess.CompletedProcess = subprocess.run(
            ['python', 'team2.py', 'columns', '--url', str(issues_6_in_sprint.url), query],
            stdout=subprocess.PIPE
        )
        assert_that(result.returncode, equal_to(0))
        lines: [str] = result.stdout.decode('utf-8').split('\n')
        assert_that(lines[0], equal_to('To Do,In Progress,Done\n'))
        assert_that(lines[1], equal_to('1,2,3\n'))


def test_smoke(mock_jira: MountebankServer, issues_6_in_sprint: Imposter):
    with mock_jira(issues_6_in_sprint) as jira_server:
        new_url=f'{str(issues_6_in_sprint.url)}/rest/api/2/search?jql=project+%3D+SCRUM1+and+sprint+in+openSprints%28%29&startAt=0&validateQuery=True&expand=changelog&maxResults=50'
        print(new_url)
        res = requests.get(new_url)
        print(res.content)
        assert_that(res.status_code, equal_to(200))
