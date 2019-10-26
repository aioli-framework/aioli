from aioli.controller.schemas import fields, Schema


class Visitor(Schema):
    id = fields.Integer()
    name = fields.String()
    location = fields.String()
    ip_addr = fields.String()


class VisitPath(Schema):
    visit_id = fields.Integer()


class VisitorPath(Schema):
    visitor_id = fields.Integer()


class Visit(Schema):
    id = fields.Integer()
    visitor = fields.Nested(Visitor)
    visited_on = fields.String()
    message = fields.String()

    class Meta:
        dump_only = ["id", "visitor", "visited_on", "created_on"]
        load_only = ["visit_id", "visitor_id"]


class VisitNew(Visit):
    message = fields.String(required=True)
    visitor_name = fields.String(required=True)
