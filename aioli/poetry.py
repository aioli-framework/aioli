from marshmallow import Schema, fields


class BuildSystemSchema(Schema):
    requires = fields.List(fields.String(), missing=["poetry>=0.12"])
    backend = fields.String(missing="poetry.masonry.api", attribute="build-backend")


class CoreSchema(Schema):
    name = fields.String(required=True)
    version = fields.String(missing="0.0.0")
    description = fields.String(required=False)
    authors = fields.List(fields.String(), missing=["Unknown User <unknown@domain.tld>"])
    license = fields.String(missing="MIT")


class PyprojectSchema(Schema):
    class Meta:
        ordered = True

    core = fields.Nested(CoreSchema, attribute="tool.poetry")
    dependencies = fields.Dict(keys=fields.Str(), values=fields.Str())
    build_system = fields.Nested(BuildSystemSchema, attribute="build-system")
