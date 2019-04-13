#!/usr/bin/env python3

import click
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
@click.option('--url', help='url of the JIRA server', required=True)
@click.option('--user', help='user in the JIRA server', required=True)
@click.option('--password', help='password in the JIRA server', required=True)
@click.pass_context
def cli(ctx: click.Context, url: str, user: str, password: str):
    ctx.ensure_object(dict)
    ctx.obj['URL'] = url
    ctx.obj['USER'] = user
    ctx.obj['PASSWORD'] = password
    pass


@cli.command()
@click.option('--col-names', '-c', 'col_names', help='name and order of the columns. Separated by :', type=str,
              required=False)
@click.option('--map', '-m', 'map_status', help='map the status to a new one for every issue', type=str, multiple=True,
              required=False)
@click.argument('query')
@click.pass_context
def columns(ctx: click.Context, col_names, map_status, query):
    j = JIRA(ctx.obj['URL'], basic_auth=(ctx.obj['USER'], ctx.obj['PASSWORD']))
    statuses = dict()

    issues = _jira_search(j, query, expand='changelog')
    for issue in issues:
        statuses[issue.fields.status.name] = statuses.get(issue.fields.status.name, 0) + 1

    if map_status is None:
        map_status = []

    for (old_column, new_column) in [item.split(':') for item in map_status]:
        if old_column in statuses:
            statuses[new_column] = statuses[old_column]
            del statuses[old_column]

    if col_names == '' or col_names is None:
        col_names = sorted(statuses.keys())
    else:
        col_names = col_names.split(":")

    header = ",".join(col_names)
    results = ",".join([str(statuses.get(i, 0)) for i in col_names])
    print(header)
    print(results)
    exit(0)


@cli.command()
@click.option('--col-names', '-c', 'col_names', help='name and order of the issue_types. Separated by :', type=str,
              required=False)
@click.argument('query')
@click.pass_context
def types(ctx: click.Context, col_names: str, query: str):
    j = JIRA(ctx.obj['URL'], basic_auth=(ctx.obj['USER'], ctx.obj['PASSWORD']))
    types = dict()
    issues = _jira_search(j, query, expand='changelog')
    for issue in issues:
        types[issue.fields.issuetype.name] = types.get(issue.fields.issuetype.name, 0) + 1

    if col_names == '' or col_names is None:
        col_names = sorted(types.keys())
    else:
        col_names = col_names.split(":")

    header = ",".join(col_names)
    results = ",".join([str(types.get(i, 0)) for i in col_names])
    print(header)
    print(results)
    exit(0)


if __name__ == '__main__':
    cli(obj={}, auto_envvar_prefix='PATRONIO')
