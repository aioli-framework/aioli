import click

from .pypi import cli_pypi
from .local import cli_local


@click.group(name="pkg", short_help="Package Management")
def cli_pkg():
    pass


cli_pkg.add_command(cli_pypi)
cli_pkg.add_command(cli_local)
