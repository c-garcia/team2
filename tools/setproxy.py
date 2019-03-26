#!/usr/bin/env python
import os

import json
import click
import requests
from dotenv import load_dotenv
from jira import JIRA, Issue
from mbtest.imposters import Imposter, Proxy
from mbtest.server import MountebankServer


def connect_proxy(proxy_url: str) -> JIRA:
    return JIRA(proxy_url, basic_auth=(os.getenv('JIRA_USER'), os.getenv('JIRA_PASSWORD')))


def create_imposter(mb_url: str, port: int, to: str) -> None:
    config = dict(
        protocol="http",
        port=port,
        stubs=[dict(
            responses=[dict(
                proxy=dict(
                    to=to,
                    predicateGenerators=[dict(matches=dict(path=True, query=True))],
                    injectHeaders={"Accept-Encoding": "identity"}
                )
            )]
        )]
    )

    print(json.dumps(config))
    resp = requests.post(f'{mb_url}', json=config)
    if resp.status_code // 100 != 2:
        raise RuntimeError(f'Problem creating imposter: {resp.content}')


def get_proxy_config(mb_url: str, port: int) -> str:
    resp = requests.get(f'{mb_url}/{port}?replayable=true&removeProxies=true')
    if resp.status_code // 100 != 2:
        raise RuntimeError('Unable to retrieve proxy configuration')
    return resp.text


def _jira_search_with_changes(j: JIRA, q: str) -> [Issue]:
    res = []
    start = 0
    while True:
        chunk = j.search_issues(q, start, expand='changelog')
        if len(chunk) == 0:
            break
        res += chunk
        start += len(chunk)
    return res


@click.command()
@click.option('--port', default=3000, help='port to listen on')
@click.option('--out', default='jiraResults.json', help='file to save')
@click.argument('query')
def setup(port, query, out):
    load_dotenv()
    server = None
    try:
        server = MountebankServer()
        create_imposter(str(server.server_url), int(port), os.getenv('JIRA_URL'))
        j = connect_proxy(f'http://localhost:{port}/')
        _jira_search_with_changes(j, query)
        proxy_config = get_proxy_config(str(server.server_url), int(port))
        with open(out, 'w') as f:
            f.write(str(proxy_config))
    finally:
        if server is not None:
            server.close()


if __name__ == '__main__':
    setup()
