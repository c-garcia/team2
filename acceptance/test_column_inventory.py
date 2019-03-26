import subprocess
from hamcrest import assert_that, equal_to


def test_shows_column_inventory(jira_123: str):
    query: str = 'project = SVP and sprint in openSprints()'
    result: subprocess.CompletedProcess = subprocess.run(
        ['python', 'team2.py', 'columns', '--url', jira_123, query],
        stdout=subprocess.PIPE
    )
    assert_that(result.returncode, equal_to(0))
    lines: [str] = result.stdout.decode('utf-8').split('\n')
    assert_that(lines[0], equal_to('To Do,In Progress,Done\n'))
    assert_that(lines[1], equal_to('1,2,3\n'))
