"""
DAOS
"""
from typing import Sequence

import jira
from furl import furl

from model import JIRAIssue, DAOException


class JIRA:
    def __init__(self, url: furl, **kwargs):
        self._url = url
        if 'api_key' not in kwargs:
            raise ValueError("No authentication option provided")
        self._username = kwargs['api_key'][0]
        self._api_key = kwargs['api_key'][1]
        self._jira = jira.JIRA(str(self._url), basic_auth=(self._username, self._api_key))

    # noinspection PyUnresolvedReferences
    @staticmethod
    def _to_issue(i: jira.Issue) -> JIRAIssue:
        return JIRAIssue(
            key=i.key,
            summary=i.fields.summary,
            status=i.fields.status.name,
            issue_type=i.fields.issuetype.name,
        )

    def query(self, query: str) -> Sequence[JIRAIssue]:
        try:
            res = []
            start = 0
            while True:
                page = self._jira.search_issues(query, startAt=start, expand='changelog')
                if len(page) == 0:
                    break
                res.extend(page)
                start += len(page)
        except Exception as e:
            raise DAOException('Error while performing query') from e
        return [self._to_issue(i) for i in res]
