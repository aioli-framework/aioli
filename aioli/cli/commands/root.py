import click

from aioli.servers import uvicorn_server


@click.group(invoke_without_command=False)
@click.pass_context
def cli_root(ctx):
    if ctx.obj is None:
        ctx.obj = {}


@cli_root.command("run", help="Start a development server")
@click.argument("app_path")
@click.option("--host", help="Bind socket to this host", default="127.0.0.1", show_default=True, type=str)
@click.option("--port",  help="Bind socket to this port", default="5000", show_default=True, type=int)
@click.option("--no_reload", help="Disable reloader", default=False, is_flag=True)
@click.option("--no_debug", help="Disable debug mode", default=False, is_flag=True)
@click.option("--workers", help="Number of workers", show_default=True, default=1, type=int)
def app_run(app_path, **kwargs):
    uvicorn_server(
        app_path,
        loop="uvloop",
        log_level="info" if kwargs.pop("no_debug") else "debug",
        reload=not kwargs.pop("no_reload"),
        workers=kwargs.pop("workers"),
        **kwargs
    )


@cli_root.command("new", short_help="Create Application")
@click.argument("app_name")
def app_new(app_name):
    print(app_name)
