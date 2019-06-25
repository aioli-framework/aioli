# -*- coding: utf-8 -*-


class ComponentMeta(type):
    _instances = {}

    def __call__(cls, pkg, *args, reuse_existing=True, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(ComponentMeta, cls).__call__(pkg, *args, **kwargs)

        return cls._instances[cls]


class Component:
    config = None
    pkg = None
    log = None

    def __init__(self, pkg):
        self.pkg = pkg
        self.app = pkg.app
        self.registry = self.app.registry
        self.log = pkg.log
        self.config = pkg.config

    async def on_startup(self):
        """Called after the Package has been successfully attached to the Application"""

    async def on_shutdown(self):
        """Called when the Application is shutting down gracefully"""
