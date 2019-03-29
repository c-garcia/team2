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
@click.option('--col-names', '--c', 'col_names', help='name and order of the columns. Separated by :', type=str, default='')
@click.argument('query')
def columns(url, col_names, query):
    load_dotenv()
    j = JIRA(url, basic_auth=(os.getenv('JIRA_USER'), os.getenv('JIRA_PASSWORD')))
    statuses = dict()
    issues = _jira_search(j, query, expand='changelog')
    for issue in issues:
        statuses[issue.fields.status.name] = statuses.get(issue.fields.status.name, 0) + 1
    if col_names == '':
        col_names = sorted(statuses.keys())
    else:
        col_names = col_names.split(":")

    header = ",".join(col_names)
    results = ",".join([str(statuses.get(i, 0)) for i in col_names])
    print(header)
    print(results)
    exit(0)


if __name__ == '__main__':
    cli()
