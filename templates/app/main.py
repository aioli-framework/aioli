import toml

import aioli
import aioli_openapi

from templates.app import example_pkg

app = aioli.Application(
    config=toml.load("aioli.cfg"),
    packages=[
        aioli_openapi,
        example_pkg,
    ]
)
