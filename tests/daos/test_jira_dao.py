"""
Tests for JIRA DAO
"""
import json

import pytest
from furl import furl
from hamcrest import assert_that, has_length, is_not, is_
from mbtest.imposters import Imposter
from mbtest.server import MountebankServer

import daos
import model


@pytest.fixture
def project_scrum1(datadir) -> Imposter:
    with open(datadir / 'all-issues-in-scrum1.json') as f:
        return Imposter.from_structure(json.load(f))


def test_new_instance_with_api_key(mock_jira: MountebankServer, project_scrum1: Imposter):
    with mock_jira(project_scrum1):
        sut = daos.JIRA(project_scrum1.url, api_key=('valid_user@example.com', 'valid_key'))
        assert_that(sut, is_not(None))


def test_new_instance_without_auth_method_throws_exception():
    with pytest.raises(ValueError):
        sut = daos.JIRA(furl('https://example.com'))
        assert_that(sut, is_not(None))


def test_query_returns_issues(mock_jira: MountebankServer, project_scrum1: Imposter):
    with mock_jira(project_scrum1):
        sut = daos.JIRA(project_scrum1.url, api_key=('jira_user', 'api_key'))
        res = sut.query('project=SCRUM1')
        assert_that(res, has_length(9))
        assert_that(all([isinstance(x, model.JIRAIssue) for x in res]), is_(True))
        assert_that(all([x.key.startswith('SCRUM') for x in res]), is_(True))
        assert_that(all([x.summary is not None for x in res]))
        assert_that(all([x.status is not None for x in res]))
        assert_that(all([x.issue_type in {'Bug', 'Task', 'Story'} for x in res]))


if __name__ == '__main__':
    pytest.main(['-vv'])
