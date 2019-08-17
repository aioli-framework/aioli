import logging
import importlib

from marshmallow import Schema, fields

from .config import PackageConfigSchema
from .controller import BaseHttpController
from .datastores import MemoryStore
from .exceptions import BootstrapException
from .service import BaseService
from .validation import (
    validate_name,
    validate_path,
    validate_description,
    validate_version
)


class PackageMetadata(Schema):
    name = fields.String(
        required=True,
        validate=validate_name
    )
    description = fields.String(
        required=False,
        validate=validate_description
    )
    version = fields.String(
        required=True,
        validate=validate_version
    )


class Package:
    """Associates components and meta with a package, for registration with a Aioli Application.

    :param meta: Package metadata, cannot be used with auto_meta
    :param auto_meta: Attempt to automatically resolve meta for Package, cannot be used with meta
    :param controllers: List of Controller classes to register with the Package
    :param services: List of Services classes to register with the Package
    :param config: Package Configuration Schema

    :ivar app: Application instance
    :ivar meta: Package meta dictionary
    :ivar log: Package logger
    :ivar config: Package config
    :ivar controllers: List of Controllers registered with the Package
    :ivar services: List of Services registered with the Package
    """

    app = None
    name = None
    state = None
    config = {}
    meta = None
    log: logging.Logger

    services = []
    controllers = []

    def __init__(
        self,
        meta=None,
        auto_meta=False,
        controllers=None,
        services=None,
        config=None,
    ):
        if auto_meta and meta:
            raise BootstrapException("Package meta and auto_meta are mutually exclude")
        elif not auto_meta and not meta:
            raise BootstrapException("Package meta or auto_meta must be supplied")

        self._meta = meta
        self._auto_meta = auto_meta

        self._services = services
        self._controllers = controllers

        if config is None:
            self.config_schema = PackageConfigSchema
        elif isinstance(config, type) and issubclass(config, PackageConfigSchema):
            self.config_schema = config
        else:
            raise BootstrapException(
                f"Invalid config type {config}. Must be subclass of {PackageConfigSchema}, or None"
            )

    def integrate_service(self, foreign_cls):
        module_name = foreign_cls.__module__.split('.')[0]
        pkg = importlib.import_module(module_name).export
        config = self.app.registry.get_config(module_name, pkg.config_schema)

        return self._register_service(
            foreign_cls,
            reuse_existing=False,
            config_override=config
        )

    def _register_logger(self, name):
        if self.app.config["debug"]:
            logger = logging.getLogger(name)
            logger.addHandler(logging._handlers["pkg_console"])
            logger.propagate = False
            logger.setLevel(logging.DEBUG)

    def _register_service(self, cls, **kwargs):
        if not issubclass(cls, BaseService):
            raise BootstrapException(
                f"Service {cls} of {self.name} is invalid, must be of {BaseService} type"
            )

        obj = cls(self, **kwargs)

        for logger in obj.loggers:
            self._register_logger(logger)

        return obj

    def _register_controller(self, cls, **kwargs):
        if not issubclass(cls, BaseHttpController):
            raise BootstrapException(
                f"Controller {cls} of {self.name} is invalid, must be of {BaseHttpController} type"
            )

        obj = cls(self, **kwargs)
        obj.register_routes(self.app.config["api_base"])
        return obj

    def _register_services(self):
        if self._services is None:
            self._services = []
        elif not isinstance(self._services, list):
            raise BootstrapException(f"{self.name} services must be a list or None")

        for cls in self._services:
            self._register_service(cls)

    def _register_controllers(self):
        if self._controllers is None:
            self._controllers = []
        elif not isinstance(self._controllers, list):
            raise BootstrapException(f"{self.name} controllers must be a list or None")

        for cls in self._controllers:
            self._register_controller(cls)

    async def call_startup_handlers(self):
        """Call startup handlers in the order they were registered (integrated services last)"""

        for svc in self.services:
            await svc.on_startup()

        for ctrl in self.controllers:
            await ctrl.on_startup()

    def register(self, app):
        self.name = name = self.meta["name"]
        self.state = MemoryStore(name)

        self.app = app
        self.log = logging.getLogger(f"aioli.pkg.{name}")

        config = self.config = app.registry.get_config(name, self.config_schema)
        config["path"] = validate_path(config.get("path", f"/{name}"))

        self._register_services()
        self._register_controllers()
