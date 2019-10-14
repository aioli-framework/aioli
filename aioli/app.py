import logging

from json.decoder import JSONDecodeError
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware

from marshmallow.exceptions import ValidationError

from aioli.exceptions import HTTPException, AioliException, BootstrapError

from .config import ApplicationConfigSchema
from .registry import ImportRegistry
from .errors import http_error, validation_error, decode_error
from .datastores import MemoryStore


class Application(Starlette):
    """Creates an Aioli application

    :param config: Configuration dictionary
    :param packages: List of packages

    :var log: Aioli Application logger
    :var registry: ImportRegistry instance
    :var config: Application config
    """

    log = logging.getLogger("aioli.core")
    state = MemoryStore("app")

    def __init__(self, packages, **kwargs):
        if not isinstance(packages, list):
            raise BootstrapError(
                f"aioli.Application expects an iterable of Packages, got: {type(packages)}"
            )

        config = kwargs.pop("config", {})
        self.__packages = packages

        try:
            self.config = ApplicationConfigSchema().load(config.get("aioli-core", {}))
        except ValueError:
            raise BootstrapError("Application `config` must be a collection")
        except ValidationError as e:
            raise BootstrapError(f"Configuration validation error: {e.messages}")

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

    def load_packages(self):
        self.log.info("Commencing countdown, engines on")
        self.registry.register_packages(self.__packages)

    async def _startup(self):
        if not self.__packages:
            self.log.warning(f"No Packages loaded")
            return

        total, failed = await self.registry.call_startup_handlers()

        if failed > 0:
            self.log.warning(f"Application degraded")
        else:
            self.log.info(f"Application ready: {total} Packages loaded")

    async def _shutdown(self):
        for pkg in self.registry.imported:
            await pkg.detach_services()
