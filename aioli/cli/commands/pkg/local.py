from collections import namedtuple

import yaml
import click
import texttable

from uvicorn import importer
from marshmallow import Schema, fields

# Package author, when looking for official packages
PKG_AUTHOR = "aioli"

# Package keyword, used for Aioli packages
PKG_KEYWORD = "aioli_package"

# Package cache lifetime in seconds
PKG_CACHE_SECS = 10


class PackageRelease(Schema):
    version = fields.String()
    upload_time = fields.DateTime()
    checksum = fields.String()
    installed = fields.Boolean(default=False)


class PackageLinks(Schema):
    pypi = fields.String()
    project = fields.String()


class PackageSchema(Schema):
    name = fields.String()
    author = fields.String()
    author_email = fields.String()
    summary = fields.String(attribute="description")
    version = fields.String()
    license = fields.String()
    links = fields.Nested(PackageLinks)
    official = fields.Boolean(default=False)
    installed = fields.Boolean(default=False)
    releases = fields.Nested(PackageRelease, many=True)


Repository = namedtuple("Repository", ["local", "remote"])


def produce_row(item, columns):
    for c in columns:
        if c == "path":
            yield item.config["path"]
        elif c in ["controllers", "services"]:
            components = getattr(item, c)
            yield len(components)
        else:
            yield item.meta[c]


def make_table(items):
    table = texttable.Texttable()

    columns = ["name", "version", "path", "controllers", "services"]
    table.add_row(columns)

    for item in items:
        row = produce_row(item, columns)
        table.add_row(list(row))

    return table


def format_controller(ctrl):
    controller = []
    for _, handler in ctrl.handlers:
        controller.append(f"{handler.method} => {handler.path} ~ {handler.description}")

    return controller


def get_one(ctx, pkg_name):
    pkg = ctx.obj["app"].obj.registry.get_import(pkg_name)
    meta = pkg.meta
    name_underline = "=" * len(pkg_name)

    props = yaml.dump(dict(
        description=meta["description"],
        version=meta["version"],
        path=pkg.config["path"],
        controllers={ctrl.__class__.__name__: format_controller(ctrl) for ctrl in pkg.controllers},
        services=[svc.__class__.__name__ for svc in pkg.services]
    ), sort_keys=False)

    return (
        "\n".join(
            [
                f"\n{pkg_name}\n{name_underline}",
                props,
            ]
        )
    )


def get_many(ctx):
    items = ctx.obj["app"].obj.registry.imported
    return make_table(items).draw()


@click.group(name="attached", short_help="Manage attached packages")
def cli_local():
    pass


@cli_local.command("show", short_help="Package details")
@click.argument("pkg_name")
@click.pass_context
def local_one(ctx, pkg_name):
    print(get_one(ctx, pkg_name))


@cli_local.command("list", short_help="List Packages")
@click.pass_context
def local_list(ctx):
    print(get_many(ctx))
