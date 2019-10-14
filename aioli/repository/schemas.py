from marshmallow import Schema, fields


class PackageRelease(Schema):
    version = fields.String()
    upload_time = fields.DateTime()
    checksum = fields.String()
    installed = fields.Boolean(default=False)


class PackageLinks(Schema):
    pypi = fields.String()
    project = fields.String()


class PackageSchema(Schema):
    name = fields.String()
    author = fields.String()
    author_email = fields.String()
    summary = fields.String(attribute="description")
    version = fields.String()
    license = fields.String()
    links = fields.Nested(PackageLinks)
    official = fields.Boolean(default=False)
    installed = fields.Boolean(default=False)
    attached = fields.Boolean(default=False)
    releases = fields.Nested(PackageRelease, many=True)

