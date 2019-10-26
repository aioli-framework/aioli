import click
import yaml

from os import getcwd

from prompt_toolkit.history import FileHistory
from click_repl import repl
from uvicorn.importer import import_from_string, ImportFromStringError

from aioli.app import Application
from aioli.cli import utils, config
from aioli.servers import uvicorn_server
from aioli.exceptions import CommandError
from aioli.datastores import FileStore
from aioli.project import TemplateInstaller, TEMPLATE_PROFILES


NON_SHELL_CMDS = ["attach", "create"]


class ProjectContext:
    db = FileStore("project")
    app_obj = None
    units = {}

    def __init__(self, app_path=None, root_dir=None):
        if not root_dir:
            self.root_dir = getcwd()

        self.app_path = app_path

    def sync_state(self):
        """Write current app_path to file for persistence"""

        self.db["app_path"] = self.app_path

    def load(self, force=False):
        """App loader

        :param force: Load even if an app_obj is already set
        """

        if not self.app_path and self.db.get("app_path"):
            self.app_path = self.db.get("app_path")
        elif (self.app_obj and not force) or not self.app_path:
            return

        try:
            app = self.app_obj = import_from_string(self.app_path)
            if not isinstance(app, Application):
                raise CommandError(f"Invalid app object. Expected: {Application}, Got: {app}")
        except ImportFromStringError as err:
            raise CommandError(f"Invalid path provided ({err})")

        app.load_units()


@click.group(invoke_without_command=False)
@click.option("--app_path", help="App to operate on, example: app:export")
@click.pass_context
def cli_root(ctx, app_path=None):
    """~ Aioli Command Line Interface ~"""

    if ctx.obj is None:
        ctx.obj = ProjectContext(app_path)

    ctx.obj.load()


@cli_root.command("attach", short_help="Attach application")
@click.pass_context
def attach_app(ctx):
    ctx.obj.sync_state()

    if not ctx.obj.app_path:
        raise CommandError("Path to an app must be supplied, example: aioli --app_path app:export attach")

    click.echo(f"Attached {ctx.obj.app_path}")


@cli_root.command("shell", help="Open application shell")
@click.pass_context
@utils.requires_app
def open_shell(ctx):
    for idx, param in enumerate(ctx.parent.command.params):
        if param.name == "app_path":
            del ctx.parent.command.params[idx]

    for cmd in NON_SHELL_CMDS:
        del ctx.parent.command.commands[cmd]

    settings = dict(
        color_depth=config.PROMPT_COLOR_DEPTH,
        style=config.PROMPT_STYLE,
        history=FileHistory(".aioli.history"),
        message=[
            ("class:prompt-name", f"[{ctx.obj.app_path}]"),
            ("class:prompt-marker", u"> "),
        ],
        # completer=ContextualCompleter()
    )

    while True:
        try:
            if not repl(ctx, prompt_kwargs=settings):
                break
        except Exception as e:
            utils.echo(f"err> {str(e)}")


@cli_root.command("start", short_help="Start development server")
@click.option("--host", help="Bind socket to this host", default="127.0.0.1", show_default=True, type=str)
@click.option("--port",  help="Bind socket to this port", default="5000", show_default=True, type=int)
@click.option("--no_reload", help="Disable reloader", default=False, is_flag=True)
@click.option("--no_debug", help="Disable debug mode", default=False, is_flag=True)
@click.option("--workers", help="Number of workers", show_default=True, default=1, type=int)
@click.pass_context
@utils.requires_app
def app_run(ctx, **kwargs):
    uvicorn_server(
        ctx.obj.app_obj,
        loop="uvloop",
        log_level="info" if kwargs.pop("no_debug") else "debug",
        reload=not kwargs.pop("no_reload"),
        workers=kwargs.pop("workers"),
        **kwargs
    )


@cli_root.command("create", short_help="Create project")
@click.option(
    "--dst_path",
    default=".",
    help="Directory in which to create the project defaults to current working directory"
)
@click.option(
    "--profile",
    help="Profile name",
    type=click.Choice(TEMPLATE_PROFILES.keys(), case_sensitive=True),
    default="minimal"
)
@click.option("--confirm", help="Confirm project creation", is_flag=True)
@click.argument("name")
def project_new(name, dst_path, confirm, profile):
    installer = TemplateInstaller(name, profile, parent_dir=dst_path)
    plan = installer.get_plan()

    if not confirm:
        summary = "{title}\n{body}\nContinue?".format(
            title=utils.get_decorated("New project"),
            body=yaml.dump(plan, sort_keys=False)
        )
        click.confirm(
            summary,
            default=True,
            abort=True
        )

    installer.write_base()
    click.echo("\nSuccess.")


@cli_root.command("info", short_help="Application info")
@click.pass_context
@utils.requires_app
def project_status(ctx):
    proj = ctx.obj
    header = utils.get_decorated("project state")

    body = yaml.dump({
        "path": proj.root_dir,
        "export": proj.app_path,
        "database": f"{ProjectContext.db.path}.db",
        #"config": proj.appconfig,
        #"metadata": proj.metadata,
        "interfaces": {
            "http": proj.app_obj.config["api_base"],
        },
        "units": [unit.name for unit in proj.app_obj.registry.imported]
    }, sort_keys=False)

    click.echo(f"{header}\n{body}")


@cli_root.command("help", short_help="Show help", hidden=True)
@click.pass_context
def show_help(ctx):
    click.echo(cli_root.get_help(ctx))
