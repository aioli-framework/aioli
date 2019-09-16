import pytest

from aioli.controller import BaseHttpController
from aioli.service import BaseService
from aioli.config import PackageConfigSchema


from aioli.exceptions import (
    BootstrapException,
    PackageConfigError,
    PackageMetaError,
)


def test_configschema_valid(get_pkg):
    class Config(PackageConfigSchema):
        pass

    assert get_pkg().config_schema == PackageConfigSchema
    assert get_pkg(config=None).config_schema == PackageConfigSchema
    assert get_pkg(config=Config).config_schema == Config


def test_configschema_invalid(get_pkg):
    with pytest.raises(BootstrapException):
        get_pkg(config=False)

    with pytest.raises(BootstrapException):
        get_pkg(config={"test": "test"})

    with pytest.raises(BootstrapException):
        get_pkg(config=[])

    with pytest.raises(BootstrapException):
        get_pkg(config=[Exception])


def test_services_register_valid(pkg):
    class Service1(BaseService):
        pass

    class Service2(BaseService):
        pass

    registered = [svc.__class__ for svc in pkg(services=[Service1, Service2]).services]
    assert Service1 in registered
    assert Service2 in registered

    assert pkg(services=[]).services == []
    assert pkg(services=None).services == []


def test_services_register_invalid(pkg):
    with pytest.raises(BootstrapException):
        pkg(services=False)

    with pytest.raises(BootstrapException):
        pkg(services={"test": "test"})

    with pytest.raises(BootstrapException):
        pkg(services=set())

    with pytest.raises(BootstrapException):
        pkg(services=[Exception])


def test_http_controllers_valid(pkg):
    class HttpController1(BaseHttpController):
        pass

    class HttpController2(BaseHttpController):
        pass

    registered = [svc.__class__ for svc in pkg(controllers=[HttpController1, HttpController2]).controllers]

    assert HttpController1 in registered
    assert HttpController2 in registered

    assert pkg(controllers=[]).controllers == []
    assert pkg(controllers=None).controllers == []


def test_controllers_invalid(pkg):
    with pytest.raises(BootstrapException):
        pkg(controllers=False)

    with pytest.raises(BootstrapException):
        pkg(controllers={"test": "test"})

    with pytest.raises(BootstrapException):
        pkg(controllers=set())

    with pytest.raises(BootstrapException):
        pkg(controllers=[Exception])


def test_version_valid(pkg):
    assert pkg(version="0.0.0").meta["version"] == "0.0.0"
    assert pkg(version="1.2.3").meta["version"] == "1.2.3"
    assert pkg(version="11.905.67").meta["version"] == "11.905.67"
    assert pkg(version="2.0.3-beta.0").meta["version"] == "2.0.3-beta.0"
    assert pkg(version="2.0.3-pre-alpha.1.2").meta["version"] == "2.0.3-pre-alpha.1.2"
    assert pkg(version="2.0.3+b.1056").meta["version"] == "2.0.3+b.1056"
    assert pkg(version="2.0.3-pre-alpha.1.2+b.1056").meta["version"] == "2.0.3-pre-alpha.1.2+b.1056"


def test_version_invalid(pkg):
    def assert_version_invalid(value):
        with pytest.raises(PackageMetaError):
            pkg(version=value)

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


def test_path_valid(pkg):
    assert pkg(conf_path="/test").config["path"] == "/test"
    assert pkg(conf_path="/test123").config["path"] == "/test123"
    assert pkg(conf_path="/test-test").config["path"] == "/test-test"


def test_path_invalid(pkg):
    def assert_path_invalid(value):
        with pytest.raises(PackageConfigError):
            pkg(conf_path=value)

        return True

    assert assert_path_invalid("test")
    assert assert_path_invalid("\\test")
    assert assert_path_invalid("\\test\\")
    assert assert_path_invalid("test/")
    assert assert_path_invalid("/test/")
    assert assert_path_invalid("/test.test")


def test_name_valid(pkg):
    len_name_str = "x" * 42

    assert pkg(name="test").meta["name"] == "test"
    assert pkg(name="test1-test2-test3").meta["name"] == "test1-test2-test3"
    assert pkg(name=len_name_str).meta["name"] == len_name_str


def test_name_invalid(pkg):
    def assert_name_invalid(value):
        with pytest.raises(PackageMetaError):
            pkg(name=value)

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


def test_description_valid(pkg):
    text = "test_description"
    assert pkg(description=text).meta["description"] == text


def test_description_invalid(pkg):
    with pytest.raises(PackageMetaError) as excinfo:
        pkg(description="a" * 257)

    assert "description" in excinfo.value.errors.keys()
