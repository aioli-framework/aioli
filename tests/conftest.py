import pytest

from aioli import Unit, Application


@pytest.fixture
def get_unit():
    def _loaded(*args, **kwargs):
        export = Unit(
            *args,
            meta=dict(
                version=kwargs.pop("version", "0.1.0"),
                name=kwargs.pop("name", "unit-name"),
                description=kwargs.pop("description", "unit_description")
            ),
            **kwargs,
        )

        return export

    return _loaded


@pytest.fixture
def get_app():
    def _loaded(units, **kwargs):
        app = Application(
            units=units,
            **kwargs
        )

        return app

    return _loaded


@pytest.fixture
def unit(get_app, get_unit, logger):
    def _loaded(*args, conf_path=None, **kwargs):
        export = get_unit(*args, **kwargs)
        config = {}

        if conf_path:
            config = {export._meta["name"]: dict(path=conf_path)}

        app = get_app([export], config=config)
        app.load_units()

        return app.registry.imported[-1]

    return _loaded


@pytest.fixture
def logger():
    import logging
    return logging.getLogger("aioli-test")
