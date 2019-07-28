import pytest

from aioli import Package, Application


@pytest.fixture
def pkg():
    def _loaded(*args, version="0.1.0", name="pkg_test", description="Test", **kwargs):
        export = Package(
            *args,
            version=version,
            name=name,
            description=description,
            **kwargs
        )

        return export

    return _loaded


@pytest.fixture
def pkg_registered(logger):
    def _loaded(path, *args, version="0.1.0", name="pkg_test", description="Test", **kwargs):
        export = Package(
            *args,
            version=version,
            name=name,
            description=description,
            **kwargs
        )

        app = Application(
            packages=[export],
            config={
                name: dict(
                    path=path
                )
            }
        )

        return app.registry.imported[-1]

    return _loaded


@pytest.fixture
def logger():
    import logging
    return logging.getLogger("aioli-test")
