import click

from .pypi import cli_pypi
from .local import cli_local


@click.group(name="pkg", short_help="Package Management")
@click.pass_context
def cli_pkg(ctx):
    pass


cli_pkg.add_command(cli_pypi)
cli_pkg.add_command(cli_local)
