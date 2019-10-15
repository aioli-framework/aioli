from aioli import Unit

from .controller import HttpController
from .service import ExampleService

export = Unit(
    controllers=[HttpController],
    services=[ExampleService],
    meta={
        "name": "whoami",
        "version": "0.0.0",
        "description": "Unit example: whoami"
    }
)
