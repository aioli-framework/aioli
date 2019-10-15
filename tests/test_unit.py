import pytest

from aioli.controller import BaseHttpController
from aioli.service import BaseService
from aioli.config import UnitConfigSchema


from aioli.exceptions import (
    BootstrapError,
    UnitConfigError,
    UnitMetaError,
)


def test_configschema_valid(get_unit):
    class Config(UnitConfigSchema):
        pass

    assert get_unit().config_schema == UnitConfigSchema
    assert get_unit(config=None).config_schema == UnitConfigSchema
    assert get_unit(config=Config).config_schema == Config


def test_configschema_invalid(get_unit):
    with pytest.raises(BootstrapError):
        get_unit(config=False)

    with pytest.raises(BootstrapError):
        get_unit(config={"test": "test"})

    with pytest.raises(BootstrapError):
        get_unit(config=[])

    with pytest.raises(BootstrapError):
        get_unit(config=[Exception])


def test_services_register_valid(unit):
    class Service1(BaseService):
        pass

    class Service2(BaseService):
        pass

    registered = [svc.__class__ for svc in unit(services=[Service1, Service2]).services]
    assert Service1 in registered
    assert Service2 in registered

    assert unit(services=[]).services == []
    assert unit(services=None).services == []


def test_services_register_invalid(unit):
    with pytest.raises(BootstrapError):
        unit(services=False)

    with pytest.raises(BootstrapError):
        unit(services={"test": "test"})

    with pytest.raises(BootstrapError):
        unit(services=set())

    with pytest.raises(BootstrapError):
        unit(services=[Exception])


def test_http_controllers_valid(unit):
    class HttpController1(BaseHttpController):
        pass

    class HttpController2(BaseHttpController):
        pass

    registered = [svc.__class__ for svc in unit(controllers=[HttpController1, HttpController2]).controllers]

    assert HttpController1 in registered
    assert HttpController2 in registered

    assert unit(controllers=[]).controllers == []
    assert unit(controllers=None).controllers == []


def test_controllers_invalid(unit):
    with pytest.raises(BootstrapError):
        unit(controllers=False)

    with pytest.raises(BootstrapError):
        unit(controllers={"test": "test"})

    with pytest.raises(BootstrapError):
        unit(controllers=set())

    with pytest.raises(BootstrapError):
        unit(controllers=[Exception])


def test_version_valid(unit):
    assert unit(version="0.0.0").meta["version"] == "0.0.0"
    assert unit(version="1.2.3").meta["version"] == "1.2.3"
    assert unit(version="11.905.67").meta["version"] == "11.905.67"
    assert unit(version="2.0.3-beta.0").meta["version"] == "2.0.3-beta.0"
    assert unit(version="2.0.3-pre-alpha.1.2").meta["version"] == "2.0.3-pre-alpha.1.2"
    assert unit(version="2.0.3+b.1056").meta["version"] == "2.0.3+b.1056"
    assert unit(version="2.0.3-pre-alpha.1.2+b.1056").meta["version"] == "2.0.3-pre-alpha.1.2+b.1056"


def test_version_invalid(unit):
    def assert_version_invalid(value):
        with pytest.raises(UnitMetaError):
            unit(version=value)

        return True

    assert assert_version_invalid("*")
    assert assert_version_invalid(">=1.2.3")
    assert assert_version_invalid("~1.2.3")
    assert assert_version_invalid("~1.2")
    assert assert_version_invalid("^0.2.4")
    assert assert_version_invalid("<2.0.0")
    assert assert_version_invalid("1.0")
    assert assert_version_invalid("1")
    assert assert_version_invalid("a.b.c")


def test_path_valid(unit):
    assert unit(conf_path="/test").config["path"] == "/test"
    assert unit(conf_path="/test123").config["path"] == "/test123"
    assert unit(conf_path="/test-test").config["path"] == "/test-test"


def test_path_invalid(unit):
    def assert_path_invalid(value):
        with pytest.raises(UnitConfigError):
            unit(conf_path=value)

        return True

    assert assert_path_invalid("test")
    assert assert_path_invalid("\\test")
    assert assert_path_invalid("\\test\\")
    assert assert_path_invalid("test/")
    assert assert_path_invalid("/test/")
    assert assert_path_invalid("/test.test")


def test_name_valid(unit):
    len_name_str = "x" * 42

    assert unit(name="test").meta["name"] == "test"
    assert unit(name="test1-test2-test3").meta["name"] == "test1-test2-test3"
    assert unit(name=len_name_str).meta["name"] == len_name_str


def test_name_invalid(unit):
    def assert_name_invalid(value):
        with pytest.raises(UnitMetaError):
            unit(name=value)

        return True

    assert assert_name_invalid("aioli")
    assert assert_name_invalid("aioli-core")
    assert assert_name_invalid("x" * 43)
    assert assert_name_invalid("test_test")
    assert assert_name_invalid("/test")
    assert assert_name_invalid("test^test")
    assert assert_name_invalid("test=test")
    assert assert_name_invalid("test/test")
    assert assert_name_invalid("test__")
    assert assert_name_invalid("__test")


def test_description_valid(unit):
    text = "test_description"
    assert unit(description=text).meta["description"] == text


def test_description_invalid(unit):
    with pytest.raises(UnitMetaError) as excinfo:
        unit(description="a" * 257)

    assert "description" in excinfo.value.errors.keys()
