from aioli.config import UnitConfigSchema, fields


class ConfigSchema(UnitConfigSchema):
    path = fields.String(missing="/guestbook")
    visits_max = fields.Integer(required=True)
