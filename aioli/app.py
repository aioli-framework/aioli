import logging
import logging.config


from json.decoder import JSONDecodeError
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware

from marshmallow.exceptions import ValidationError

from aioli.exceptions import HTTPException, AioliException, BootstrapException
from aioli.log import LOGGING_CONFIG_DEFAULTS

from .config import ApplicationConfigSchema
from .registry import ImportRegistry
from .errors import http_error, validation_error, decode_error
from .__state import State


class Application(Starlette):
    """Creates an Aioli application

    :param config: Configuration dictionary
    :param packages: List of packages

    :var log: Aioli Application logger
    :var registry: ImportRegistry instance
    :var config: Application config
    """

    log = logging.getLogger("aioli.core")
    state = State("app")

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

    def _register_packages(self):
        self.registry.register_packages(self.__packages)

    async def _startup(self):
        self.log.info("Commencing countdown, engines on")

        if not self.__packages:
            self.log.warning(f"No Packages loaded")
            return

        try:
            self._register_packages()
        except Exception as e:
            self.log.exception(e)
            self.log.critical("Fatal error during bootstrapping")
            return

        total, failed = await self.registry.call_startup_handlers()

        if failed > 0:
            self.log.warning(f"Application degraded")
        else:
            self.log.info(f"Application ready: {total} Packages loaded")

    async def _shutdown(self):
        for pkg in self.registry.imported:
            await pkg.detach_services()
