# -*- coding: utf-8 -*-

from enum import Enum

import logging
import logging.config
import traceback

import ujson

from json.decoder import JSONDecodeError
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import Response
from marshmallow.exceptions import ValidationError

from aioli.exceptions import HTTPException, AioliException
from aioli.log import LOGGING_CONFIG_DEFAULTS
from aioli.package import Package

from .config import ApplicationConfigSchema


def jsonify(content, status=200):
    return Response(
        content=ujson.dumps(content, ensure_ascii=False).encode("utf8"),
        status_code=status,
        headers={"content-type": "application/json"},
    )


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
    imported = {}
    log = logging.getLogger("aioli.pkg")

    def __init__(self, modules, conf_full):
        self._conf_full = conf_full
        self._modules = set(modules)

    def _get_components(self, comp_type, pkg_name=None):
        comp_type = ComponentType(comp_type).name

        if pkg_name:
            return getattr(self.imported[pkg_name], comp_type)

        comps = []

        for pkg, _ in self.imported.values():
            comps += getattr(pkg, comp_type)

        return comps

    def get_services(self, pkg_name=None):
        return [(svc.__class__, svc) for svc in self._get_components("service", pkg_name)]

    async def attach_to(self, app):
        for module in self._modules:
            if not hasattr(module, "export"):
                raise Exception(f"Missing export member of class {Package} in {module}")

            package = module.export

            self.log.info(f"Attaching {package.name}/{package.version}")

            if not isinstance(package, Package):
                raise Exception(f"Invalid package type {package}: must be of type {Package}")

            config = self._conf_full.get(package.name, {})

            await package.register(app, config)

            self.imported.update({package.name: (package, module)})

        for pkg, _ in self.imported.values():
            await pkg.attach_controllers()
            await pkg.attach_services()


class Application(Starlette):
    """Creates an Aioli application

    :param config: Configuration dictionary
    :param packages: List of package tuples [(<mount path>, <module>), ...]
    :param kwargs: Keyword arguments to pass along to Starlette

    :var log: Aioli Application logger
    :var packages: Packages registered with the Application
    """

    log = logging.getLogger("aioli.core")
    packages = None
    __state = {}

    def __init__(self, packages, **kwargs):
        if not isinstance(packages, list):
            raise Exception(
                f"aioli.Application expects an iterable of Packages, got: {type(packages)}"
            )

        config = kwargs.pop("config", {})

        self.registry = ImportRegistry(packages, config)

        try:
            self.config = ApplicationConfigSchema().load(config.get("aioli", {}))
        except ValueError:
            raise Exception("Application `config` must be a collection")
        except ValidationError as e:
            raise Exception(f"Configuration validation error: {e.messages}")

        for name, logger in LOGGING_CONFIG_DEFAULTS['loggers'].items():
            self.log_level = logger['level'] = 'DEBUG' if self.config.get('debug') else 'INFO'

        logging.config.dictConfig(LOGGING_CONFIG_DEFAULTS)

        # Apply known settings from environment or provided `config`
        super(Application, self).__init__(**kwargs)

        # Lifespan handlers
        self.router.lifespan.add_event_handler("startup", self._startup)
        self.router.lifespan.add_event_handler("shutdown", self._shutdown)

        # Error handlers
        self.add_exception_handler(AioliException, http_error)
        self.add_exception_handler(HTTPException, http_error)
        self.add_exception_handler(ValidationError, validation_error)
        self.add_exception_handler(JSONDecodeError, decode_error)
        self.add_exception_handler(Exception, server_error)

        # Middleware
        self.add_middleware(CORSMiddleware, allow_origins=["*"])

    def add_exception_handler(self, exception, handler):
        """Add a new exception handler

        :param exception: Exception class
        :param handler: Exception handler
        """

        return super(Application, self).add_exception_handler(exception, handler)

    async def _startup(self):
        try:
            self.log.info("Commencing countdown, engines on")

            await self.registry.attach_to(self)
            self.log.info(f"Loaded {len(self.registry.imported)} packages ~ Ready for action!")
        except Exception as e:
            self.log.critical(traceback.format_exc())
            raise e

    async def _shutdown(self):
        for mod, pkg in self.packages.attached:
            await pkg.detach_services()
