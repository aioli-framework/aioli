from .standard import StandardConfig


class GuesthouseConfig(StandardConfig):
    extra = {
        "guestbook": dict(
            visits_max=10
        ),
        "aioli-rdbms": dict(
            type="mysql",
            username="root",
            password="testar123",
            host="127.0.0.1",
            port=3306,
            database="aioli"
        ),
        "aioli-openapi": dict(
            path="/openapi",
            oas_version="3.0.2"
        )
    }
    dependencies = {
        "python": "^3.6",
        "aioli-rdbms": "^0.3.4",
        "aioli-openapi": "^0.3.0"
    }
