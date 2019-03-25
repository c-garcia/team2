import subprocess
from hamcrest import assert_that, equal_to


def test_shows_column_inventory(jira_123):
    result = subprocess.run(['python', 'columns.py', '--project', 'SVP'], stdout=subprocess.PIPE)
    assert_that(result.returncode, equal_to(0))
    lines = result.stdout.decode('utf-8').split('\n')
    assert_that(lines[0], equal_to('To Do,In Progress,Done\n'))
    assert_that(lines[1], equal_to('1,2,3\n'))
