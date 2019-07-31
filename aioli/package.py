import logging
import re

from marshmallow import Schema, fields, validate
from marshmallow.exceptions import ValidationError

from .controller import BaseHttpController, BaseWebSocketController
from .service import BaseService
from .config import PackageConfigSchema
from .exceptions import BootstrapException, InvalidPackagePath, InvalidPackageName


NAME_REGEX = r"^[a-z0-9]+(?:_[a-z0-9]+)*$"

# Semantic version regex
# 1 - Major
# 2 - Minor
# 3 - Patch
# 4 (optional) - Pre-release version info
# 5 (optional) - Metadata (build time, number, etc.)

VERSION_REGEX = r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(-[a-zA-Z\d][-a-zA-Z.\d]*)?(\+[a-zA-Z\d][-a-zA-Z.\d]*)?$"


class PackageMetadata(Schema):
    name = fields.String(
        required=True,
        validate=[
            validate.Regexp(
                NAME_REGEX,
                error="The Package name may contain up to 42 lowercase alphanumeric and underscore characters."
            ),
            validate.Length(max=42)
        ]
    )
    description = fields.String(
        required=False,
        validate=validate.Length(max=256)
    )
    version = fields.String(
        required=True,
        validate=validate.Regexp(
            VERSION_REGEX,
            error="Invalid Semantic Versioning string"
        )
    )


class Package:
    """Associates components and meta with a package, for registration with a Aioli Application.

    :param meta: Package metadata.
    :param auto_meta: Attempt to automatically resolve meta for Package
    :param controllers: List of Controller classes to register with the Package
    :param services: List of Services classes to register with the Package
    :param config: Package Configuration Schema

    :ivar app: Application instance
    :ivar log: Package logger
    :ivar state: Package state
    :ivar config: Package config
    :ivar controllers: List of Controllers registered with the Package
    :ivar services: List of Services registered with the Package
    """

    class State:
        __state = {}

        def __setitem__(self, key, value):
            self.__state[key] = value

        def __getitem__(self, item):
            return self.__state.get(item)

    app = None
    path = None
    config = {}
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
        elif not auto_meta or meta:
            raise BootstrapException("Package meta or auto_meta must be supplied")

        self.meta = PackageMetadata().loads(meta) if meta else None
        self.auto_meta = auto_meta

        self.__controllers = controllers
        self.__services = services

        if config is None:
            self.conf_schema = PackageConfigSchema
        elif isinstance(config, type) and issubclass(config, PackageConfigSchema):
            self.conf_schema = config
        else:
            raise BootstrapException(
                f"Invalid config type {config}. Must be subclass of {PackageConfigSchema}, or None"
            )

        self.state = Package.State()

    async def detach_services(self):
        for svc in self.services:
            await svc.on_shutdown()

    async def attach_services(self):
        for svc in self.services:
            await svc.on_startup()

    async def attach_controllers(self):
        for ctrl in self.controllers:
            ctrl.register_routes(self.app.config["api_base"])
            await ctrl.on_startup()

    # @TODO - Create common registration method
    def _register_services(self, pkg_name):
        registered = []

        if not self.__services and not isinstance(self.__services, list):
            raise BootstrapException(f"{pkg_name} services must be a list or None")

        for svc in self.__services:
            if not issubclass(svc, BaseService):
                raise BootstrapException(f"{pkg_name} services must be a list of BaseService services")

            registered.append(svc(self))

        self.services = set(registered)

    # @TODO - Create common registration method
    def _register_controllers(self, pkg_name):
        registered = []

        if not self.__controllers and not isinstance(self.__controllers, list):
            raise BootstrapException(f"{pkg_name} controllers must be a list or None")

        for ctrl in self.__controllers:
            if not issubclass(ctrl, BaseHttpController) or issubclass(ctrl, BaseWebSocketController):
                raise BootstrapException(f"{pkg_name} controllers must be a list of "
                                         f"{BaseHttpController} or {BaseWebSocketController} controllers")

            registered.append(ctrl(self))

        self.controllers = set(registered)

    def register(self, app, config):
        name = self.meta["name"]
        path = self.config.get("path", f"/{name}")

        if name in ["aioli", "aioli_core"]:
            raise InvalidPackageName(f"Name {name} is reserved and cannot be used")

        if re.match(r"^/[a-zA-Z0-9-_]*$", path):
            self.path = path
        else:
            raise InvalidPackagePath(f"Invalid path was provided to Package {name}")

        self.app = app
        self.log = logging.getLogger(f"aioli.pkg.{name}")

        try:
            self.config = self.conf_schema(name).load(config)
        except ValidationError as e:
            raise BootstrapException(f"Package {name} failed configuration validation: {e.messages}")

        self._register_services(name)
        self._register_controllers(name)
