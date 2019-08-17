from .component import Component, ComponentMeta
from .exceptions import BootstrapException


class BaseService(Component, metaclass=ComponentMeta):
    """Base Service class

    :param pkg: Attach to this package

    :var app: Application instance
    :var registry: Application ImportRegistry
    :var pkg: Parent Package
    :var config: Package configuration
    :var log: Package logger
    """

    _instances = {}
    loggers = []

    async def _on_startup(self):
        return await self.on_startup()

    def _validate_import(self, svc):
        if not issubclass(svc, BaseService):
            raise BootstrapException(
                f"{svc.__name__} passed to {self.__class__.__name__}.use_service is "
                f"not a subclass of aioli.{BaseService.__name__}"
            )
        elif svc not in self._instances.keys():
            pkg_name = svc.__module__.split('.')[0]
            raise BootstrapException(
                f"Package {pkg_name}, used by Service {svc.__name__}, must be registered with the Application"
            )

    def connect(self, svc):
        """Reuses existing instance of the given Service class, in the context of
        the Package it was first registered with.


        :param svc: Service class
        :return: Existing Service instance
        """

        self._validate_import(svc)
        return self._instances[svc]

    def integrate(self, svc_cls):
        """Creates a new instance of the given Service class in the context of the current Package.

        :param svc_cls: Service class
        :return: Service instance
        """

        self._validate_import(svc_cls)
        self.pkg.add_relation(svc_cls, self)

        svc = svc_cls(pkg=self.pkg, reuse_existing=False)

        return svc

