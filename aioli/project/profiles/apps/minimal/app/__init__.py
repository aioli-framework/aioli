import toml

import aioli


export = aioli.Application(
    config=toml.load("app.toml"),
    units=[]
)
