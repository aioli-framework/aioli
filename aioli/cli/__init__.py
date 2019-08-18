import click

from .commands import (
    pkg_group,
    app_group
)


@click.group(invoke_without_command=False)
@click.pass_context
def cli_app(ctx):
    if ctx.obj is None:
        ctx.obj = {}


# Add groups
cli_app.add_command(pkg_group)
cli_app.add_command(app_group)
