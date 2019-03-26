#!/usr/bin/env python3

import click


@click.group()
def cli():
    pass


@cli.command()
@click.option('--url', help='url of the JIRA server')
@click.argument('query')
def columns(url, query):
    click.echo("Not implemented")
    exit(1)


if __name__ == '__main__':
    cli()
