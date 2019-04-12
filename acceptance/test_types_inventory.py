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
def issues_3_in_sprint(datadir, mock_jira) -> Imposter:
    with open(datadir / 'jira.json', 'r') as f:
        return Imposter.from_structure(json.load(f))


def test_shows_types_inventory(mock_jira: MountebankServer, issues_3_in_sprint: Imposter):
    query: str = 'project=SCRUM2 and sprint in openSprints()'
    with mock_jira(issues_3_in_sprint):
        result: subprocess.CompletedProcess = subprocess.run(
            ['python', 'team2.py', 'types', '--url', str(issues_3_in_sprint.url), query],
            stdout=subprocess.PIPE
        )
        assert_that(result, completed_successfully())
        assert_that(result, has_header_with_columns_in_lexicographical_order(['Bug', 'Story']))
        assert_that(result, output_cell_has_value(0, 'Bug', 1))
        assert_that(result, output_cell_has_value(0, 'Story', 2))

