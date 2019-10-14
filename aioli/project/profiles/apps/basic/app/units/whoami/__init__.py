from aioli import Package

from .controller import HttpController
from .service import ExampleService

export = Package(
    controllers=[HttpController],
    services=[ExampleService],
    meta={
        "name": "whoami",
        "version": "0.0.0",
        "description": "Example whoami package"
    }
)
