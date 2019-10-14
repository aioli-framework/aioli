import click

from aioli.cli import utils

from .pypi import cli_pypi
from .local import cli_local


@click.group(name="units", short_help="Unit Management")
@click.pass_context
@utils.requires_app
def cli_pkg(ctx):
    pass


cli_pkg.add_command(cli_pypi)
cli_pkg.add_command(cli_local)
