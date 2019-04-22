#!/usr/bin/env python3

import click
from furl import furl
from jira import JIRA, Issue
import sys

from typing import Mapping
from dataclasses import replace

import daos
import dates
import model
import writers


def _map_status(i: model.JIRAIssue, m: Mapping[str, str]) -> model.JIRAIssue:
    if i.status in m:
        return replace(i, status=m[i.status])
    return i


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
    ctx.obj['JIRA'] = daos.JIRA(furl(url), api_key=(user, password))


@cli.command()
@click.option('--col-name', '-c', 'col_names', help='name and order of the columns. Separated by :', type=str,
              required=False, multiple=True)
@click.option('--map', '-m', 'map_status', help='map the status to a new one for every issue',
              type=click.Tuple([str, str]), nargs=2, required=False, multiple=True, )
@click.argument('query')
@click.pass_context
def columns(ctx: click.Context, col_names, map_status, query):
    try:
        issues = ctx.obj['JIRA'].query(query)
        map_status_mapping = {x: y for (x, y) in map_status}
        new_issues = [_map_status(i, map_status_mapping) for i in issues]
        statuses = dict()
        for issue in new_issues:
            # noinspection PyUnresolvedReferences
            statuses[issue.status] = statuses.get(issue.status, 0) + 1

        if col_names == () or col_names is None:
            col_names = sorted(statuses.keys())

        writers.CSV.write_map(sys.stdout, statuses, keys=col_names, default='0')
        sys.exit(0)
    except model.DAOException as e:
        click.echo(f'Error retrieving backlog items: {e.message}', err=True, nl=True)
        sys.exit(1)


@cli.command()
@click.option('--col-names', '-c', 'col_names', help='name and order of the issue_types. Separated by :', type=str,
              required=False)
@click.argument('query')
@click.pass_context
def types(ctx: click.Context, col_names: str, query: str):
    j = JIRA(ctx.obj['URL'], basic_auth=(ctx.obj['USER'], ctx.obj['PASSWORD']))
    issue_types = dict()
    issues = _jira_search(j, query, expand='changelog')
    for issue in issues:
        # noinspection PyUnresolvedReferences
        issue_types[issue.fields.issuetype.name] = issue_types.get(issue.fields.issuetype.name, 0) + 1

    if col_names == '' or col_names is None:
        col_names = sorted(issue_types.keys())
    else:
        col_names = col_names.split(":")

    header = ",".join(col_names)
    results = ",".join([str(issue_types.get(i, 0)) for i in col_names])
    print(header)
    print(results)
    exit(0)


@cli.command()
@click.option('--project', '-p', 'project', type=str, help='Key of the project', required=True)
@click.option('--start-date', '-s', 'start_date', type=click.DateTime(formats=['%Y-%m-%d', '%Y/%m/%d']),
              help='Start date in format YYYY-mm-dd', required=True)
@click.option('--end-date', '-e', 'end_date', type=click.DateTime(formats=['%Y-%m-%d', '%Y/%m/%d']),
              help='End date in format YYYY-mm-dd', required=True)
@click.option('--inventory-statuses', '-i', 'inventory_statuses', type=str, required=True,
              help='Comma-separated list of statuses that are considered Inventory')
@click.option('--done-statuses', '-i', 'done_statuses', type=str, required=True,
              help='Comma-separated list of statuses that are considered Done')
@click.pass_context
def flow_time(ctx: click.Context, project, start_date, end_date, inventory_statuses, done_statuses):
    j = JIRA(ctx.obj['URL'], basic_auth=(ctx.obj['USER'], ctx.obj['PASSWORD']))
    date_list = dates.relevant_days_between(start_date, end_date)
    accumulated_inventory = 0
    accumulated_flow_rate = 0
    for date in date_list:
        jira_formatted_date = dates.jira_date(date)
        inventory_query = f'project={project} and status was in ("{inventory_statuses}") on "{jira_formatted_date}"'
        accumulated_inventory += len(_jira_search(j, inventory_query, expand='changelog'))
        done_query = f'project={project} and status changed to ("{done_statuses}") on "{jira_formatted_date}"'
        accumulated_flow_rate += len(_jira_search(j, done_query, expand='changelog'))

    if accumulated_flow_rate == 0:
        avg_flow_rate = float('nan')
    else:
        avg_flow_rate = accumulated_inventory / accumulated_flow_rate

    print("Flow time")
    print(f'{avg_flow_rate:0.2f}')
    exit(0)


if __name__ == '__main__':
    cli(obj={}, auto_envvar_prefix='PATRONIO')
