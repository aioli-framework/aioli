import pytest

from aioli import Package, Application


@pytest.fixture
def get_pkg():
    def _loaded(*args, **kwargs):
        export = Package(
            *args,
            meta=dict(
                version=kwargs.pop("version", "0.1.0"),
                name=kwargs.pop("name", "pkg_name"),
                description=kwargs.pop("description", "pkg_description")
            ),
            **kwargs,
        )

        return export

    return _loaded


@pytest.fixture
def get_app():
    def _loaded(packages, **kwargs):
        app = Application(
            packages=packages,
            **kwargs
        )

        return app

    return _loaded


@pytest.fixture
def pkg(get_app, get_pkg, logger):
    def conf_path(value):
        return dict(config={"path": value})

    def _loaded(*args, conf_path=None, **kwargs):
        export = get_pkg(*args, **kwargs)
        config = {}

        if conf_path:
            config = {export._meta["name"]: dict(path=conf_path)}

        app = get_app([export], config=config)
        app._load_packages()

        return app.registry.imported[-1]

    return _loaded


@pytest.fixture
def logger():
    import logging
    return logging.getLogger("aioli-test")
