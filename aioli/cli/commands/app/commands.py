import click
import texttable

from uvicorn import run as run_server, importer


@click.group(name="app", short_help="Application operations")
@click.pass_context
def app_group(ctx):
    pass


@app_group.command("new", short_help="Create a new application")
@click.pass_context
def app_new(ctx, **kwargs):
    pass


@app_group.command("start", help="Start the development server")
@click.option("--host", help="Bind socket to this host", default="127.0.0.1", show_default=True, type=str)
@click.option("--port",  help="Bind socket to this port", default="5000", show_default=True, type=int)
@click.option("--no_reload", help="Disable reloader", default=False, is_flag=True)
@click.option("--no_debug", help="Disable debug mode", default=False, is_flag=True)
@click.option("--workers", help="Number of workers", show_default=True, default=1, type=int)
@click.option(
    "--path",
    help="Example: app=Application(...) in my_proj/__main__.py becomes --path my_proj:app",
    required=True,
    show_default=True,
    type=str
)
def dev_start(path, host, port, **kwargs):
    config = importer.import_from_string(path).config

    run_server(
        path,
        host=host or config["dev_host"],
        port=port or config["dev_port"],
        loop="uvloop",
        log_level="info" if kwargs.pop("no_debug") else "debug",
        reload=not kwargs.pop("no_reload"),
        workers=kwargs.pop("workers", 1)
    )
