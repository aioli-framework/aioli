import os
import configparser
import logging
import logging.config

from importlib_metadata import metadata
from enum import Enum

from json.decoder import JSONDecodeError
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware

from marshmallow.exceptions import ValidationError

from aioli.exceptions import HTTPException, AioliException, BootstrapException
from aioli.log import LOGGING_CONFIG_DEFAULTS
from aioli.package import Package, PackageMetadata

from .config import ApplicationConfigSchema
from .utils import jsonify


async def server_error(_, exc):
    if isinstance(exc, NotImplementedError):
        message = "Not implemented"
    else:
        message = "Internal server error"

    return jsonify({"message": message}, status=500)


async def validation_error(_, exc):
    return jsonify({"message": exc.messages}, status=422)


async def decode_error(*_):
    return jsonify({"message": "Error decoding JSON"}, status=400)


async def http_error(_, exc):
    return jsonify({"message": exc.detail}, status=exc.status_code)


class ComponentType(Enum):
    services = "service"
    controllers = "controller"


class ImportRegistry:
    imported = []
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

            if package.auto_meta and hasattr(registerable, "__path__"):
                pyproject_path = os.path.join(registerable.__path__[0], "..", "pyproject.toml")

                if os.path.exists(pyproject_path):
                    parser = configparser.ConfigParser()
                    parser.read(pyproject_path)
                    pyproject = parser["tool.poetry"]
                    meta = {k: v.strip('"') for k, v in pyproject.items() if k in ["name", "description", "version"]}
                elif hasattr(registerable, "__name__"):
                    dist = dict(metadata(registerable.__name__))
                    meta = dict(
                        name=dist.get("Name"),
                        version=dist.get("Version"),
                        description=dist.get("Summary")
                    )
                else:
                    raise BootstrapException(f"Unable to find metadata for {registerable}")

                package.meta = PackageMetadata().load(meta)

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


class Application(Starlette):
    """Creates an Aioli application

    :param config: Configuration dictionary
    :param packages: List of package tuples [(<mount path>, <module>), ...]
    :param kwargs: Keyword arguments to pass along to Starlette

    :var log: Aioli Application logger
    :var packages: Packages registered with the Application
    """

    log = logging.getLogger("aioli.core")
    __state = {}

    def __init__(self, packages, **kwargs):
        if not isinstance(packages, list):
            raise BootstrapException(
                f"aioli.Application expects an iterable of Packages, got: {type(packages)}"
            )

        config = kwargs.pop("config", {})
        self.__packages = packages

        try:
            self.config = ApplicationConfigSchema().load(config.get("aioli_core", {}))
        except ValueError:
            raise BootstrapException("Application `config` must be a collection")
        except ValidationError as e:
            raise BootstrapException(f"Configuration validation error: {e.messages}")

        for name, logger in LOGGING_CONFIG_DEFAULTS['loggers'].items():
            self.log_level = logger['level'] = 'DEBUG' if self.config.get('debug') else 'INFO'

        logging.config.dictConfig(LOGGING_CONFIG_DEFAULTS)

        self.registry = ImportRegistry(self, config)

        # Apply known settings from environment or provided `config`
        super(Application, self).__init__(debug=self.config["debug"], **kwargs)

        # Error handlers
        self.add_exception_handler(AioliException, http_error)
        self.add_exception_handler(HTTPException, http_error)
        self.add_exception_handler(ValidationError, validation_error)
        self.add_exception_handler(JSONDecodeError, decode_error)

        # Middleware
        self.add_middleware(CORSMiddleware, allow_origins=self.config["allow_origins"])

        # Lifespan handlers
        self.router.lifespan.add_event_handler("startup", self._startup)
        self.router.lifespan.add_event_handler("shutdown", self._shutdown)

    def add_exception_handler(self, exception, handler):
        """Add a new exception handler

        :param exception: Exception class
        :param handler: Exception handler
        """

        return super(Application, self).add_exception_handler(exception, handler)

    async def _startup(self):
        self.log.info("Commencing countdown, engines on")

        self.registry.register_packages(self.__packages)

        self.log.debug("## Calling startup handlers ##")

        total, failed = await self.registry.call_startup_handlers()

        if failed > 0:
            self.log.warning(f"Application degraded")
        else:
            self.log.info(f"{total} Packages loaded ~ Ready for action!")

    async def _shutdown(self):
        for pkg in self.registry.imported:
            await pkg.detach_services()
