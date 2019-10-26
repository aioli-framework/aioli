import toml

import aioli
import aioli_openapi
import aioli_rdbms

from .units import guestbook


export = aioli.Application(
    config=toml.load("app.toml"),
    units=[
        guestbook,
        aioli_openapi,
        aioli_rdbms
    ]
)
