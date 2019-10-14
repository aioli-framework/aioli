import toml

import aioli
import aioli_openapi

from .units import whoami as example_unit

export = aioli.Application(
    config=toml.load("app.toml"),
    packages=[
        example_unit,
        aioli_openapi,
    ]
)
