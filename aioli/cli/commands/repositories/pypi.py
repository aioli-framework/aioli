from pathlib import Path

import yaml
import click
import texttable

from aioli.cli import config, utils
from aioli.datastores import FileStore
from aioli.exceptions import CommandError
from aioli.repository import Repository


def produce_row(item, columns):
    for c in columns:
        if c in ["official", "attached", "installed"]:
            yield "YES" if item[c] else "NO"
        else:
            yield item[c]


def make_table(items):
    table = texttable.Texttable()

    columns = ["name", "description", "official", "installed", "attached"]
    table.add_row(columns)

    for item in items.values():
        row = produce_row(item, columns)
        table.add_row(list(row))

    return table


def get_many(ctx, **kwargs):
    unit = ctx.obj.units["pypi"]
    units = unit.get_many(**kwargs)

    if not units:
        raise CommandError("No Aioli packages found")

    table = make_table(units)

    return "\n" + table.draw() + "\n"


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

    props = yaml.dump(dict(
        description=unit["description"],
        author="{0} <{1}>".format(unit.pop("author"), unit.pop("author_email")),
        license=unit["license"],
        links=unit["links"],
        releases=sorted(releases, reverse=True)[:4],
    ), sort_keys=False)

    return (
        "\n".join(
            [
                f"\n{utils.get_underlined(name)}",
                props,
            ]
        )
    )


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
    click.echo(get_one(ctx, unit_name))


@cli_pypi.command("list", short_help="List Units")
@click.pass_context
def pypi_list(ctx):
    click.echo(get_many(ctx))


@cli_pypi.command("download", short_help="Download unit package")
@click.pass_context
def pypi_download(ctx):
    click.echo("Work in progress")
