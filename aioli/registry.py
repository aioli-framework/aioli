import os
import logging
import configparser

from enum import Enum

from importlib_metadata import metadata

from .exceptions import BootstrapException
from .package import Package, PackageMetadata


class ComponentType(Enum):
    services = "service"
    controllers = "controller"


class ImportRegistry:
    imported = []
    integrations = {}
    log = logging.getLogger("aioli.pkg")

    def __init__(self, app, config):
        self._config = config
        self._app = app

    def _get_components(self, comp_type, pkg_name=None):
        comp_type = ComponentType(comp_type).name

        if pkg_name:
            return getattr(self.imported[pkg_name], comp_type)

        comps = []

        for _, module in self.imported:
            comps += getattr(module.export, comp_type)

        return comps

    def get_services(self, pkg_name=None):
        return [(svc.__class__, svc) for svc in self._get_components("service", pkg_name)]

    def register_packages(self, registerables):
        registerables = set(registerables)

        for registerable in registerables:
            if isinstance(registerable, Package):
                package = registerable
            elif hasattr(registerable, "export"):
                package = registerable.export
            else:
                raise BootstrapException(
                    f"Expected an Aioli-type Python Package, or an aioli.Package, got: {registerable}"
                )

            meta = None

            if package._auto_meta and hasattr(registerable, "__path__"):
                pyproject_file = "pyproject.toml"
                self.log.debug(f"Looking for project metadata [auto_meta]")
                pyproject_path = os.path.join(registerable.__path__[0], "..", pyproject_file)

                if os.path.exists(pyproject_path):  # Meta from pyproject
                    parser = configparser.ConfigParser()
                    parser.read(pyproject_path)
                    pyproject = parser["tool.poetry"]
                    meta = {k: v.strip('"') for k, v in pyproject.items() if k in ["name", "description", "version"]}
                elif hasattr(registerable, "__name__"):  # Meta from dist
                    dist = dict(metadata(registerable.__name__))
                    meta = dict(
                        name=dist.get("Name").replace("-", "_"),
                        version=dist.get("Version"),
                        description=dist.get("Summary")
                    )
            elif package._meta:
                meta = package._meta
            else:
                raise BootstrapException(f"Unable to find metadata for {registerable}")

            try:
                package.meta = PackageMetadata().load(meta)
            except BootstrapException as e:
                self.log.exception(e)
                raise

            self.log.info("Attaching {name}/{version}".format(**package.meta))

            config = self._config.get(package.meta["name"], {})
            package.register(self._app, config)

            self.imported.append(package)

    async def call_startup_handlers(self):
        total = failed = 0

        for package in self.imported:
            total += 1

            try:
                await package.call_startup_handlers()
            except Exception:
                failed += 1
                pkg_name = package.meta['name']
                self.log.exception(f"When calling startup hooks for {pkg_name}:")

        return total, failed
