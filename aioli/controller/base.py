from starlette.endpoints import WebSocketEndpoint

from aioli.component import Component, ComponentMeta
from aioli.exceptions import BootstrapException
from aioli.utils import format_path

from .registry import handlers


class HttpControllerMeta(ComponentMeta):
    def __call__(cls, pkg, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(ComponentMeta, cls).__call__(pkg, *args, **kwargs)

        obj = cls._instances[cls]

        if obj not in pkg.services:
            pkg.controllers.append(obj)

        return obj


class BaseHttpController(Component, metaclass=HttpControllerMeta):
    """HTTP API Controller

    :param pkg: Attach to this package

    :var pkg: Parent Package
    :var config: Package configuration
    :var log: Controller logger
    """

    async def on_request(self, *args):
        """Called on request arrival for this Controller"""

    def register_routes(self, api_base):
        for func, handler in self.handlers:
            handler_addr = hex(id(func))
            handler_name = f"{self.__class__.__name__}.{handler.name}"

            path_full = format_path(api_base, self.config["path"], handler.path)

            if not hasattr(self, "pkg"):
                raise BootstrapException(f"Superclass of {self} was never created")

            self.log.info(
                f"Adding Route: {path_full} [{handler.method}] => "
                f"{handler.name} [{handler_addr}]"
            )

            methods = [handler.method]

            self.pkg.app.add_route(path_full, func, methods, handler_name)
            handler.path_full = path_full

    @property
    def handlers(self):
        for handler in handlers.values():
            # Yield only if the stack belongs to the Controller being iterated on
            if handler.func.__module__ == self.__module__:
                yield getattr(self, handler.name), handler


class BaseWebSocketController(WebSocketEndpoint, Component, metaclass=ComponentMeta):
    path = None
    encoding = "json"
