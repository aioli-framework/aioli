from .base import ProfileConfig


class StandardConfig(ProfileConfig):
    export_obj = "export"
    http_api = "/api/v1"
    metadata = "pyproject.toml"
    appconfig = "app.toml"
    extra = None
    dependencies = {"python": "^3.6"}
