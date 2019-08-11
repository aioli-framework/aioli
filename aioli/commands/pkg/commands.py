import os

from collections import namedtuple
from pathlib import Path

import click
import texttable

from yaml import load, dump
from aioli import package_state
from poetry.utils.env import Env

from marshmallow import Schema, fields, pre_dump, pre_load, post_load
from poetry.repositories.pypi_repository import PyPiRepository, Package, ServerProxy
from poetry.repositories.installed_repository import InstalledRepository

from poetry.repositories.exceptions import PackageNotFound

from aioli.exceptions import CommandException

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


class PackageIndex:
    """
    Class for interacting with a remote PyPI index.

    Due to the somewhat flimsy design of PyPI Warehouse Web APIs, we're forced to write
    some seemingly convoluted code in this class.
    """

    url = "https://pypi.python.org/pypi"
    packages_all = {}

    def __init__(self, path):
        proj_env = Env(path)
        self.repository = Repository(
            local=InstalledRepository().load(proj_env),
            remote=PyPiRepository()
        )

    def get_installed(self, name):
        return self.repository.local.find_packages(name)

    def _pull(self, **query):
        index = ServerProxy(self.url)
        official = True if query.get("authors") == [PKG_AUTHOR] else False

        for p in index.search(query):
            p["official"] = official
            p["installed"] = len(self.get_installed(p["name"])) > 0
            info = PackageSchema(unknown="EXCLUDE").load(p)
            yield info["name"], info

    def get_many(self, force_refresh=False, **query):
        pkgs = package_state["pypi_all"]

        if not force_refresh and pkgs:
            return package_state["pypi_all"]

        query.update({"keywords": [PKG_KEYWORD]})

        # Get all Aioli Packages
        new_state = dict([p for p in self._pull(**query)])

        # "tag" official Aioli packages *sigh*
        new_state.update(dict([p for p in self._pull(**query, authors=[PKG_AUTHOR])]))

        package_state["pypi_all"] = new_state

        return new_state

    def get_one(self, name):
        pkgs = self.get_many()
        pkg = pkgs.get(name)

        if not pkg:
            raise CommandException("No package by that name was found")
        elif "releases" in pkg:
            return pkg

        pkg_data = self.repository.remote.get_package_info(name)
        info = pkg_data["info"]
        releases = pkg_data["releases"]

        pkg_full = PackageSchema(unknown="EXCLUDE").load(
            dict(
                **info,
                links=dict(
                    project=info.pop("home_page").rstrip("/"),
                    pypi=info.pop("project_url").rstrip("/")
                ),
                releases=[dict(
                    installed=pkg["installed"] and pkg["version"] == version,
                    version=version,
                    checksum=dist[0].get("md5_digest"),
                    upload_time=dist[0].get("upload_time"),
                ) for version, dist in releases.items()]
            )
        )

        package_state["pypi_all"][name] = pkg_full

        return pkg_full


def get_table_row(item, columns):
    for c in columns:
        if c in ["official", "installed"]:
            yield "YES" if item[c] else "NO"
        else:
            yield item[c]


def get_table(items):
    table = texttable.Texttable()

    columns = ["name", "description", "official", "installed"]
    table.add_row(columns)

    for item in items.values():
        row = get_table_row(item, columns)
        table.add_row(list(row))

    return table


@click.group(name="pkg", short_help="Package management")
@click.pass_context
def pkg_group(ctx):
    path = Path(".")
    ctx.obj["idx"] = PackageIndex(path)


@pkg_group.command("show", short_help="Show details about an Aioli Package")
@click.argument("pkg_name")
@click.pass_context
def pkg_show(ctx, pkg_name):
    idx = ctx.obj["idx"]
    pkg = idx.get_one(pkg_name)
    name = pkg["name"]
    underline = "=" * len(name)

    releases = []

    for release in pkg.pop("releases"):
        version = release["version"]
        upload_time = release["upload_time"]
        installed = " [installed]" if release["installed"] else ""

        releases.append(f"{version} ({upload_time})" + installed)

    del pkg["version"]

    props = dump(dict(
        description=pkg["description"],
        author="{0} <{1}>".format(pkg.pop("author"), pkg.pop("author_email")),
        license=pkg["license"],
        links=pkg["links"],
        releases=sorted(releases, reverse=True)[:4],
    ), sort_keys=False)

    print(
        "\n".join(
            [
                f"\n{name}\n{underline}",
                props,
            ]
        )
    )


@pkg_group.command("list", short_help="List Aioli Packages")
@click.pass_context
def pkg_list(ctx, **kwargs):
    idx = ctx.obj["idx"]
    pkgs = idx.get_many(**kwargs)

    if not pkgs:
        raise CommandException("No Aioli packages found")

    table = get_table(pkgs)

    print(
        "\n".join(
            [
                "",
                table.draw(),
                "\nPackage details: aioli pkg show <PKG_NAME>\n",
            ]
        )
    )

