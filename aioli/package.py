import logging

from marshmallow import Schema, fields

from .controller import BaseHttpController
from .service import BaseService
from .component import ComponentMeta
from .config import PackageConfigSchema
from .exceptions import BootstrapException
from .validation import (
    validate_name,
    validate_path,
    validate_description,
    validate_version
)
from .__state import State


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
            self._conf_schema = PackageConfigSchema
        elif isinstance(config, type) and issubclass(config, PackageConfigSchema):
            self._conf_schema = config
        else:
            raise BootstrapException(
                f"Invalid config type {config}. Must be subclass of {PackageConfigSchema}, or None"
            )

    def _register_services(self):
        if self._services is None:
            self._services = []
        elif not isinstance(self._services, list):
            raise BootstrapException(f"{self.name} services must be a list or None")

        for svc in self._services:
            if type(svc) != ComponentMeta or not issubclass(svc, BaseService):
                raise BootstrapException(
                    f"Service {svc} of {self.name} is invalid, must be of {BaseService} type"
                )

            obj = svc(self)
            yield obj

    def _register_controllers(self):
        if self._controllers is None:
            self._controllers = []
        elif not isinstance(self._controllers, list):
            raise BootstrapException(f"{self.name} controllers must be a list or None")

        for ctrl in self._controllers:
            if type(ctrl) != ComponentMeta or not issubclass(ctrl, BaseHttpController):
                raise BootstrapException(
                    f"Controller {ctrl} of {self.name} is invalid, must be of {BaseHttpController} type"
                )

            obj = ctrl(self)
            obj.register_routes(self.app.config["api_base"])
            yield obj

    async def call_startup_handlers(self):
        for svc in self.services:
            await svc.on_startup()

        for ctrl in self.controllers:
            await ctrl.on_startup()

    def register(self, app, config):
        self.name = name = self.meta["name"]
        self.state = State(name)

        config["path"] = validate_path(config.get("path", f"/{name}"))

        self.app = app
        self.log = logging.getLogger(f"aioli.pkg.{name}")

        self.config = self._conf_schema(name).load(config)

        self.services = set(self._register_services())
        self.controllers = set(self._register_controllers())
