from os import environ as env

from marshmallow import fields, post_load, schema, validate


class ConfigMeta(schema.SchemaMeta):
    def __new__(mcs, *args, **kwargs):
        return super(ConfigMeta, mcs).__new__(mcs, *args, **kwargs)


class BaseConfigSchema(schema.Schema, metaclass=ConfigMeta):
    def __init__(self, prefix, *args, **kwargs):
        super(BaseConfigSchema, self).__init__(*args, **kwargs)
        self.prefix = prefix

    @post_load
    def format_data(self, data, **_):
        params = {}

        for param, field in data.items():
            env_param = self.prefix + param.upper()

            if env_param in env:  # Prefer environ
                value = env.get(env_param)
                if isinstance(field, fields.Integer):
                    value = int(value)
                if isinstance(field, fields.Boolean):
                    value = str(value).strip().lower() in ["1", "true", "yes"]
            else:
                value = data[param]

            params[param] = value

        return params


class PackageConfigSchema(BaseConfigSchema):
    """Package configuration schema

    :var debug: Set debug level for package, effectively overriding Application's debug level
    :var path: Package path, uses Package name if empty
    :var should_import_services: Setting to False skips Service registration for this Package
    :var should_import_controllers: Setting to False skips Controller registration for this Package
    """

    def __init__(self, *args, **kwargs):
        super(PackageConfigSchema, self).__init__(*args, **kwargs)

    debug = fields.Bool(missing=None)
    path = fields.String(required=False, missing=None)
    should_import_controllers = fields.Bool(missing=True)
    should_import_services = fields.Bool(missing=True)


class ApplicationConfigSchema(BaseConfigSchema):
    """Application configuration schema

    :var dev_host: Development server listen host
    :var dev_port: Development server listen port
    :var debug: Debug mode
    :var path: Application base path
    """

    def __init__(self, *args, **kwargs):
        super(ApplicationConfigSchema, self).__init__("AIOLI_", *args, **kwargs)

    dev_host = fields.String(missing="127.0.0.1")
    dev_port = fields.Integer(missing=5000)
    pretty_json = fields.Bool(missing=False)
    allow_origins = fields.List(fields.String(), missing=["*"])
    debug = fields.Bool(missing=True)
    path = fields.String(missing="/api", attribute="api_base")
