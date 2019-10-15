from .component import Component, ComponentMeta
from .exceptions import BootstrapError


class ServiceMeta(ComponentMeta):
    def __call__(cls, unit, *args, reuse_existing=True, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(ComponentMeta, cls).__call__(unit, *args, **kwargs)

        obj = cls._instances[cls]

        if obj not in unit.services:
            unit.services.append(obj)

        return obj


class BaseService(Component, metaclass=ServiceMeta):
    """Base Service class

    :param unit: Attach to this unit

    :var app: Application instance
    :var registry: Application ImportRegistry
    :var unit: Parent Unit
    :var config: Unit configuration
    :var log: Unit logger
    """

    _instances = {}
    loggers = []

    def connect(self, cls):
        """Reuses existing instance of the given Service class, in the context of
        the Unit it was first registered with.


        :param cls: Service class
        :return: Existing Service instance
        """

        if cls not in self._instances.keys():
            unit_name = cls.__module__.split('.')[0]
            raise BootstrapError(
                f"Unit {unit_name}, used by Service {cls.__name__}, must be registered with the Application"
            )

        return self._instances[cls]

    def integrate(self, cls):
        """Creates a new instance of the given Service class in the context of the current Unit.

        :param cls: Service class
        :return: Integrated Service
        """

        return self.unit.integrate_service(cls)
