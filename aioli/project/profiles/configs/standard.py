from .base import ProfileConfig


class StandardProfileConfig(ProfileConfig):
    app_dir = "app"
    export_obj = "export"
    http_api = "/api/v1"
    metadata = "pyproject.toml"
    appconfig = "app.toml"
