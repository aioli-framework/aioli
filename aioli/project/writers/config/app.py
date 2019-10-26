import toml

from aioli.config import ApplicationConfigSchema, UnitConfigSchema


class ConfigSchema(UnitConfigSchema):
    class Meta:
        unknown = "INCLUDE"


def appconfig(output_path, core=None, extra=None):
    extra = extra and dict(extra) or {}

    data = {
        "aioli-core": ApplicationConfigSchema().load(core or {}),
        **extra
    }

    with open(output_path, mode="w") as fh:
        return toml.dump(data, fh)
