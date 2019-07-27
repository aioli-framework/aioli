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

    def _validate_import(self, svc):
        assert issubclass(svc, BaseService), (
            f"{svc.__name__} passed to {self.__class__.__name__}.use_service is "
            f"not a subclass of aioli.{BaseService.__name__}"
        )

        if svc not in self._instances.keys():
            raise BootstrapException(f"Cannot use unregistered Service: {svc.__name__}")

    def connect(self, svc):
        """Reuses existing instance of the given Service class, in the context of
        the Package it was first registered with.


        :param svc: Service class
        :return: Existing Service instance
        """

        self._validate_import(svc)
        return self._instances[svc]

    def integrate(self, svc):
        """Creates a new instance of the given Service class in the context of the current Package.

        :param svc: Service class
        :return: Service instance
        """

        self._validate_import(svc)
        return svc(pkg=self.pkg, reuse_existing=False)
