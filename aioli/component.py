class ComponentMeta(type):
    _instances = {}

    def __call__(cls, unit, *args, reuse_existing=True, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(ComponentMeta, cls).__call__(unit, *args, **kwargs)

        return cls._instances[cls]


class Component:
    config = None
    unit = None
    log = None

    def __init__(self, unit, config_override=None):
        self.unit = unit
        self.app = unit.app
        self.registry = self.app.registry
        self.log = unit.log
        self.config = config_override or unit.config

    async def on_startup(self):
        """Called after the Unit has been successfully attached to the Application and the Loop is available"""

    async def on_shutdown(self):
        """Called when the Application is shutting down gracefully"""
