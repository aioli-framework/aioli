import click

from .pypi import Pypi


@click.group(name="pkg", short_help="Package management")
def pkg_group():
    pass


@pkg_group.command("list", short_help="List Aioli Packages")
def pkg_list(**kwargs):
    pkgs = Pypi()
    print(pkgs.packages)
