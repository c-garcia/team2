#!/usr/bin/env python3

import os

import click
from dotenv import load_dotenv
from jira import JIRA, Issue


def _jira_search(j: JIRA, q: str, **kwargs) -> [Issue]:
    res = []
    start = 0
    expand = kwargs.get('expand', 0)
    while True:
        chunk = j.search_issues(q, start, expand=expand)
        if len(chunk) == 0:
            break
        res += chunk
        start += len(chunk)
    return res


@click.group()
def cli():
    pass


@cli.command()
@click.option('--url', help='url of the JIRA server')
@click.argument('query')
def columns(url, query):
    load_dotenv()
    j = JIRA(url, basic_auth=(os.getenv('JIRA_USER'), os.getenv('JIRA_PASSWORD')))
    statuses = dict()
    issues = _jira_search(j, query, expand='changelog')
    for issue in issues:
        statuses[issue.fields.status.name] = statuses.get(issue.fields.status.name, 0) + 1
    header = ",".join(sorted(statuses.keys()))
    results = ",".join([str(statuses.get(i, 0)) for i in sorted(statuses.keys())])
    print(header)
    print(results)
    exit(0)


if __name__ == '__main__':
    cli()
