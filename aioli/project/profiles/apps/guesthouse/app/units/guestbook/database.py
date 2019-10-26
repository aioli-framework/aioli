import datetime

from aioli_rdbms.model import Model, fields


class VisitorModel(Model):
    __tablename__ = "visitor"

    id = fields.Integer(primary_key=True)
    name = fields.String(index=True, max_length=64)
    ip_addr = fields.String(index=True, max_length=15)
    location = fields.String(allow_null=True, max_length=64)


class VisitModel(Model):
    __tablename__ = "visit"

    id = fields.Integer(primary_key=True)
    visited_on = fields.DateTime(default=datetime.datetime.utcnow)
    message = fields.String(max_length=64)
    visitor = fields.ForeignKey(VisitorModel)
