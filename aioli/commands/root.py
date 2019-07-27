import logging

import click

from uvicorn import run as run_server, importer


@click.group()
def cli():
    pass


@click.command()
@click.option("--host", help="Bind socket to this host.")
@click.option("--port",  help="Bind socket to this port.")
@click.option("--reload", default=True)
@click.option("--workers", default=1)
@click.option("--debug", default=True)
@click.argument("app_path")
def dev_server(app_path, host, port, debug, **kwargs):
    config = importer.import_from_string(app_path).config

    run_server(
        app_path,
        host=host or config["dev_host"],
        port=port or config["dev_port"],
        loop="uvloop",
        log_level="debug" if debug else "info",
        **kwargs
    )


cli.add_command(dev_server)
