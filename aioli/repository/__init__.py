import logging

from sys import stdout
from collections import namedtuple

from poetry.repositories.pypi_repository import PyPiRepository, ServerProxy
from poetry.repositories.installed_repository import InstalledRepository
from poetry.utils.env import Env

from aioli.exceptions import CommandError

from .schemas import PackageSchema


# Package author, when looking for official packages
PKG_AUTHOR = "aioli"

# Package keyword, used for Aioli packages
PKG_KEYWORD = "aioli_package"

RepositoryCollection = namedtuple("Repository", ["installed", "remote"])


class Repository:
    """
    For interacting with a remote PyPI index.

    Due to the somewhat flimsy design of PyPI Warehouse Web APIs, we're forced to write
    some seemingly convoluted code in this class.
    """

    url = "https://pypi.python.org/pypi"
    packages_all = {}
    log = logging.getLogger("pypi")

    def __init__(self, directory, state, config, attached):
        self.attached = attached
        self.state = state
        self.config = config
        proj_env = Env(directory)
        self.repository = RepositoryCollection(
            installed=InstalledRepository().load(proj_env),
            remote=PyPiRepository()
        )

    def get_installed(self, name):
        return self.repository.installed.find_packages(name)

    def _pull(self, **query):
        index = ServerProxy(self.url)
        official = True if query.get("authors") == [PKG_AUTHOR] else False

        for p in index.search(query):
            p["official"] = official
            p["installed"] = len(self.get_installed(p["name"])) > 0
            p["attached"] = p["name"] in [a.name for a in self.attached]
            info = PackageSchema(unknown="EXCLUDE").load(p)
            yield info["name"], info

    def get_many(self, force_refresh=False, **query):
        pkgs = self.state["pypi_all"]

        if not force_refresh and pkgs:
            return self.state["pypi_all"]

        stdout.write("\nPulling fresh data from PyPI...")

        query.update({"keywords": [PKG_KEYWORD]})

        # Get all Aioli Packages
        new_state = dict([p for p in self._pull(**query)])

        # "tag" official Aioli packages *sigh*
        new_state.update(dict([p for p in self._pull(**query, authors=[PKG_AUTHOR])]))

        stdout.write(f"storing for {self.config.PYPI_LIFETIME_SECS}s\n")
        self.state["pypi_all"] = new_state

        return new_state

    def get_one(self, name):
        pkgs = self.get_many()
        pkg = pkgs.get(name)

        if not pkg:
            raise CommandError("No package by that name was found")
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

        self.state["pypi_all"][name] = pkg_full

        return pkg_full
