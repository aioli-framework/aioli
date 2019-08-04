import click

from uvicorn import run as run_server, importer


@click.group(invoke_without_command=False)
def root_group():
    pass


@click.command(name="dev-start", help="Start development server")
@click.option("--host", help="Bind socket to this host", default="127.0.0.1", show_default=True, type=str)
@click.option("--port",  help="Bind socket to this port", default="5000", show_default=True, type=int)
@click.option("--no_reload", help="Disable reloader", default=False, type=bool)
@click.option("--no_debug", help="Disable debug mode", default=False, type=bool)
@click.option("--workers", help="Number of workers", show_default=True, default=1, type=int)
@click.option(
    "--path",
    help="Example: app=Application(...) in my_proj/__main__.py becomes --path my_proj:app",
    required=True,
    show_default=True,
    type=str
)
def dev_start(path, host, port, **kwargs):
    kwargs["reload"] = not kwargs.pop("no_reload")
    kwargs["debug"] = not kwargs.pop("no_debug")

    config = importer.import_from_string(path).config

    run_server(
        path,
        host=host or config["dev_host"],
        port=port or config["dev_port"],
        loop="uvloop",
        log_level="debug" if kwargs["debug"] else "info",
        **kwargs
    )
