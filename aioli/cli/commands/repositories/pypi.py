from pathlib import Path

import yaml
import click

from aioli.cli import config, utils, table
from aioli.datastores import FileStore
from aioli.exceptions import CommandError
from aioli.repository import Repository


class PypiTable(table.BaseTable):
    def get_row(self, item):
        for c in self.columns:
            if c in ["official", "attached", "installed"]:
                yield "YES" if item[c] else "NO"
            else:
                yield item[c]


def get_many(ctx, **kwargs):
    unit = ctx.obj.units["pypi"]
    units = unit.get_many(**kwargs)

    if not units:
        raise CommandError("No Aioli packages found")

    return PypiTable(
        ["name", "description", "official", "installed", "attached"],
        units.values()
    ).draw()


def get_one(ctx, unit_name):
    unit = ctx.obj.units["pypi"].get_one(unit_name)
    name = unit["name"]
    releases = []

    for release in unit.pop("releases"):
        version = release["version"]
        upload_time = release["upload_time"]
        attached = " [attached]" if name in ctx.obj.app_obj.registry.imported else ""
        releases.append(f"{version} ({upload_time})" + attached)

    del unit["version"]

    unit_info = yaml.dump(dict(
        description=unit["description"],
        author="{0} <{1}>".format(unit.pop("author"), unit.pop("author_email")),
        license=unit["license"],
        links=unit["links"],
        releases=sorted(releases, reverse=True)[:4],
    ), sort_keys=False)

    return utils.get_section(title=unit_name, body=unit_info)


@click.group(name="pypi", short_help="Units available on PyPI")
@click.pass_context
def cli_pypi(ctx):
    ctx.obj.units["pypi"] = Repository(
        Path("."),
        FileStore("units", lifetime_secs=config.PYPI_LIFETIME_SECS),
        config,
        ctx.obj.app_obj.registry.imported
    )


@cli_pypi.command("show", short_help="Unit details")
@click.argument("unit_name")
@click.pass_context
def pypi_one(ctx, unit_name):
    utils.echo(get_one(ctx, unit_name))


@cli_pypi.command("list", short_help="List Units")
@click.pass_context
def pypi_list(ctx):
    utils.echo(get_many(ctx), pad_bottom=True)
