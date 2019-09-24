import click

from click_repl import repl
from uvicorn.importer import import_from_string

from aioli import cli
from aioli.servers import uvicorn_server


class ApplicationModel:
    __path = None
    __obj = None

    @property
    def path(self):
        return self.__path

    @path.setter
    def path(self, value):
        self.__obj = import_from_string(value)
        self.__obj.load_packages()
        self.__path = value

    @property
    def obj(self):
        return self.__obj


class MissingApplicationError(Exception):
    pass


def requires_app(func):
    def func_wrapper(ctx, *args, **kwargs):
        if ctx.obj["app"] is None:
            raise MissingApplicationError(f"Command [{ctx.command.name}] requires an Application to be set")

        return func(ctx, *args, **kwargs)

    return func_wrapper


@click.group(invoke_without_command=False)
@click.option(
    "--app_path",
    help="Path to Application to operate on",
    type=str
)
@click.pass_context
def cli_root(ctx, app_path=None):
    if ctx.obj is None:
        ctx.obj = {
            "app": ApplicationModel()
        }
    if app_path:
        ctx.obj["app"].path = app_path


@cli_root.command("shell", help="Opens a shell for the given Application")
@click.pass_context
def open_shell(ctx):
    app_name = ctx.obj["app"].path or "NO APP"

    # The shell handles app state; remove the "--app_path" root cli option.
    for idx, param in enumerate(ctx.parent.command.params):
        if param.name == "app_path":
            del ctx.parent.command.params[idx]

    settings = dict(
        color_depth=cli.config.PROMPT_COLOR_DEPTH,
        style=cli.config.PROMPT_STYLE,
        message=[
            ("class:prompt-name", f"[{app_name}]"),
            ("class:prompt-marker", u"> "),
        ]
    )

    repl(ctx, prompt_kwargs=settings)


@cli_root.command("start", short_help="Start a development server")
@click.option("--host", help="Bind socket to this host", default="127.0.0.1", show_default=True, type=str)
@click.option("--port",  help="Bind socket to this port", default="5000", show_default=True, type=int)
@click.option("--no_reload", help="Disable reloader", default=False, is_flag=True)
@click.option("--no_debug", help="Disable debug mode", default=False, is_flag=True)
@click.option("--workers", help="Number of workers", show_default=True, default=1, type=int)
@click.pass_context
@requires_app
def app_run(ctx, **kwargs):
    uvicorn_server(
        ctx.obj["app"].obj,
        loop="uvloop",
        log_level="info" if kwargs.pop("no_debug") else "debug",
        reload=not kwargs.pop("no_reload"),
        workers=kwargs.pop("workers"),
        **kwargs
    )


@cli_root.command("new", short_help="Create new Aioli application")
@click.argument("app_name")
def app_new(app_name):
    import aioli

    print(aioli.__path__)


@cli_root.command("help", short_help="Show help", hidden=True)
@click.pass_context
def show_help(ctx):
    print(cli_root.get_help(ctx))
