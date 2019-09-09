from aioli import Package

from .controller import HttpController
from .service import ExampleService

export = Package(
    controllers=[HttpController],
    services=[ExampleService],
    meta={
        "name": "example_pkg",
        "version": "0.1.0",
    }
)
