from marshmallow import Schema, fields


class UnitRelease(Schema):
    version = fields.String()
    upload_time = fields.DateTime()
    checksum = fields.String()
    installed = fields.Boolean(default=False)


class UnitLinks(Schema):
    pypi = fields.String()
    project = fields.String()


class UnitSchema(Schema):
    name = fields.String()
    author = fields.String()
    author_email = fields.String()
    summary = fields.String(attribute="description")
    version = fields.String()
    license = fields.String()
    links = fields.Nested(UnitLinks)
    official = fields.Boolean(default=False)
    installed = fields.Boolean(default=False)
    attached = fields.Boolean(default=False)
    releases = fields.Nested(UnitRelease, many=True)

