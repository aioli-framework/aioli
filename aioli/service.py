from .component import Component, ComponentMeta
from .exceptions import BootstrapException


class ServiceMeta(ComponentMeta):
    def __call__(cls, pkg, *args, reuse_existing=True, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(ComponentMeta, cls).__call__(pkg, *args, **kwargs)

        obj = cls._instances[cls]

        if obj not in pkg.services:
            pkg.services.append(obj)

        return obj


class BaseService(Component, metaclass=ServiceMeta):
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

    def connect(self, cls):
        """Reuses existing instance of the given Service class, in the context of
        the Package it was first registered with.


        :param cls: Service class
        :return: Existing Service instance
        """

        if cls not in self._instances.keys():
            pkg_name = cls.__module__.split('.')[0]
            raise BootstrapException(
                f"Package {pkg_name}, used by Service {cls.__name__}, must be registered with the Application"
            )

        return self._instances[cls]

    def integrate(self, cls):
        """Creates a new instance of the given Service class in the context of the current Package.

        :param cls: Service class
        :return: Integrated Service
        """

        return self.pkg.integrate_service(cls)
