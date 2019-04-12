#!/usr/bin/env python
import json
import os

import click
import requests
from dotenv import load_dotenv
from jira import JIRA, Issue
from mbtest.server import MountebankServer


def connect_proxy(proxy_url: str) -> JIRA:
    return JIRA(proxy_url, basic_auth=(os.getenv('JIRA_USER'), os.getenv('JIRA_PASSWORD')))


def create_imposter(mb_url: str, port: int, to: str, user: str) -> None:
    config = dict(
        protocol="http",
        port=port,
        stubs=[dict(
            responses=[dict(
                proxy=dict(
                    to=to,
                    predicateGenerators=[dict(matches=dict(path=True, query=True))],
                    injectHeaders={"Accept-Encoding": "identity"}
                ),
                #function escapeRegExp(text) { return text.replace(/[-[\]{}()*+?.,\\^$|#\s]/g, '\\$&'); }
                _behaviors=dict(
                    decorate="""
(config) => {{
    const randomString = () => Math.trunc(Math.random() * 1000000).toString();
    const escapeRegExp = (text) => text.replace(/[-[\\]{{}}()*+?.,\\\\^$|#\\s]/g, '\\\\$&');
    const accountId = 'fabadafabadafabadafabada';
    const origAccountId = config.response.headers['X-AACCOUNTID'];
    
    if (origAccountId){{
      config.response.headers['X-AACCOUNTID'] = accountId;
      config.response.body = config.response.body.replace(new RegExp(origAccountId, 'g'), accountId);
    }}
    if (config.response.headers['X-AREQUESTID']){{
      config.response.headers['X-AREQUESTID'] = randomString();
    }}
    if (config.response.headers['ATL-TraceId']){{
      config.response.headers['ATL-TraceId'] = randomString();
    }}
    if (config.response.headers['Set-Cookie']){{
      config.response.headers['Set-Cookie'] = "atlassian.xsrf.token=a-random-token_lin; Path=/; Secure";
    }}
    const usr_re=new RegExp(escapeRegExp('{1}'), 'g');
    config.response.body = config.response.body.replace(usr_re, 'some_user@no-domain.example.com')
    const url_re=new RegExp('{0}', 'g');
    config.response.body = config.response.body.replace(url_re, 'https://non-existing-server.example.com')
    const avatar_re = /avatar-cdn.atlassian.com\\/([a-z0-9]+)/;
    const avatar_matches = avatar_re.exec(config.response.body)
    if (avatar_matches){{
        config.response.body = config.response.body.replace(new RegExp(avatar_matches[1], 'g'), '00');
    }}
    const displayname_re = /("displayName"):"([^"]*)"/g;
    config.response.body = config.response.body.replace(displayname_re, '$1:"No Name"')
    config.response.body = config.response.body.replace(/"(\\d\\dx\\d\\d)":"[^"]*"/g, '"$1":"https//avatar.example.com/1.jpg"'); 
}}
""".format(to, user)
                )

            )]
        )]
    )

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
        create_imposter(str(server.server_url), int(port), os.getenv('JIRA_URL'), os.getenv('JIRA_USER'))
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
