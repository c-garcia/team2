import io

import pytest
from click.testing import CliRunner
from hamcrest import assert_that, is_, instance_of, contains, has_key, equal_to

import daos
import model
import team2
import writers
from model import JIRAIssue

QUERY = 'project = XXXX'
ISSUES = [
    JIRAIssue(key='XXX-1', summary='s1', issue_type='Story', status='To Do'),
    JIRAIssue(key='XXX-2', summary='s2', issue_type='Story', status='To Do'),
    JIRAIssue(key='XXX-3', summary='s3', issue_type='Bug', status='In Progress'),
    JIRAIssue(key='XXX-4', summary='s4', issue_type='Bug', status='Done'),
    JIRAIssue(key='XXX-5', summary='s5', issue_type='Task', status='Done'),
    JIRAIssue(key='XXX-6', summary='s6', issue_type='Task', status='Done'),
]
VALID_CREDENTIALS = ['--url', 'https://example.com', '--user', 'valid_user', '--password', 'valid_password']


def test_calls_dao_and_outputs_results(mocker):
    mock_jira = mocker.Mock(spec=daos.JIRA)
    mock_jira.query = mocker.Mock(return_value=ISSUES)
    mocker.patch('daos.JIRA', return_value=mock_jira)
    mock_writer = mocker.patch('writers.CSV', spec=writers.CSV)
    output = CliRunner().invoke(
        team2.cli,
        [*VALID_CREDENTIALS, 'columns', '-c', 'To Do', '-c', 'In Progress', '-c', 'Done', QUERY]
    )
    mock_jira.query.assert_called_once_with(QUERY)
    mock_writer.write_map.assert_called_once()
    args, kwargs = mock_writer.write_map.call_args
    assert_that(args[0], instance_of(io.IOBase))
    assert_that(args[1], contains('To Do', 'In Progress', 'Done'))
    assert_that(kwargs, has_key('keys'))
    assert_that(kwargs['keys'], contains('To Do', 'In Progress', 'Done'))
    assert_that(kwargs, has_key('default'))
    assert_that(kwargs['default'], equal_to('0'))
    assert_that(output.exit_code, is_(0))


def test_error_in_dao_is_shown_in_stderr(mocker):
    mock_jira = mocker.Mock(spec=daos.JIRA)
    mock_jira.query = mocker.Mock(side_effect=model.DAOException('Some JIRA error'))
    mocker.patch('daos.JIRA', return_value=mock_jira)
    mock_writer = mocker.patch('writers.CSV', spec=writers.CSV)
    mock_echo = mocker.patch('click.echo')
    output = CliRunner().invoke(
        team2.cli,
        [*VALID_CREDENTIALS, 'columns', '-c', 'To Do', '-c', 'In Progress', '-c', 'Done', QUERY],
        mix_stderr=True
    )
    assert_that(output.exit_code, is_(1))
    mock_echo.assert_called_with('Error retrieving backlog items: Some JIRA error', nl=True, err=True)
    mock_writer.write_map.assert_not_called()


if __name__ == '__main__':
    pytest.main(['-vv'])
