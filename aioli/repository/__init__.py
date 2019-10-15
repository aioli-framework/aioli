import logging

from sys import stdout
from collections import namedtuple

from poetry.repositories.pypi_repository import PyPiRepository, ServerProxy
from poetry.repositories.installed_repository import InstalledRepository
from poetry.utils.env import Env

from aioli.exceptions import CommandError

from .schemas import UnitSchema


# Package author, when looking for official package
PKG_AUTHOR = "aioli"

# Package keyword, used for Aioli packages
PKG_KEYWORD = "aioli_package"

RepositoryCollection = namedtuple("Repository", ["local", "remote"])


class Repository:
    """
    For interacting with a remote PyPI index.

    Due to the somewhat flimsy design of PyPI Warehouse Web APIs, we're forced to write
    some seemingly convoluted code in this class.
    """

    url = "https://pypi.python.org/pypi"
    units_all = {}
    log = logging.getLogger("pypi")

    def __init__(self, directory, state, config, attached):
        self.attached = attached
        self.state = state
        self.config = config
        proj_env = Env(directory)
        self.repository = RepositoryCollection(
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
            p["attached"] = p["name"] in [a.name for a in self.attached]
            info = UnitSchema(unknown="EXCLUDE").load(p)
            yield info["name"], info

    def get_many(self, force_refresh=False, **query):
        units = self.state["pypi_all"]

        if not force_refresh and units:
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
        units = self.get_many()
        unit = units.get(name)

        if not unit:
            raise CommandError("No Unit by that name was found")
        elif "releases" in unit:
            return unit

        unit_data = self.repository.remote.get_package_info(name)
        info = unit_data["info"]
        releases = unit_data["releases"]

        unit_full = UnitSchema(unknown="EXCLUDE").load(
            dict(
                **info,
                links=dict(
                    project=info.pop("home_page").rstrip("/"),
                    pypi=info.pop("project_url").rstrip("/")
                ),
                releases=[dict(
                    installed=unit["installed"] and unit["version"] == version,
                    version=version,
                    checksum=dist[0].get("md5_digest"),
                    upload_time=dist[0].get("upload_time"),
                ) for version, dist in releases.items()]
            )
        )

        self.state["pypi_all"][name] = unit_full

        return unit_full
