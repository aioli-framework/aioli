import pytest

from aioli.controller import BaseHttpController, BaseWebSocketController
from aioli.service import BaseService
from aioli.config import PackageConfigSchema


from aioli.exceptions import (
    BootstrapException,
    InvalidPackageName,
    InvalidPackageVersion,
    InvalidPackagePath,
    InvalidPackageDescription
)


def test_configschema_valid(get_pkg):
    class Config(PackageConfigSchema):
        pass

    assert get_pkg()._conf_schema == PackageConfigSchema
    assert get_pkg(config=None)._conf_schema == PackageConfigSchema
    assert get_pkg(config=Config)._conf_schema == Config


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

    assert pkg(services=[]).services == set()
    assert pkg(services=None).services == set()


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

    assert pkg(controllers=[]).controllers == set()
    assert pkg(controllers=None).controllers == set()


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
    with pytest.raises(InvalidPackageVersion):
        pkg(version="*")

    with pytest.raises(InvalidPackageVersion):
        pkg(version=">=1.2.3")

    with pytest.raises(InvalidPackageVersion):
        pkg(version="~1.2.3")

    with pytest.raises(InvalidPackageVersion):
        pkg(version="~1.2")

    with pytest.raises(InvalidPackageVersion):
        pkg(version="^0.2.4")

    with pytest.raises(InvalidPackageVersion):
        pkg(version="<2.0.0")

    with pytest.raises(InvalidPackageVersion):
        pkg(version="1.0")

    with pytest.raises(InvalidPackageVersion):
        pkg(version="1")

    with pytest.raises(InvalidPackageVersion):
        pkg(version="a.b.c")


def test_path_valid(pkg):
    assert pkg(conf_path="/test").config["path"] == "/test"
    assert pkg(conf_path="/test123").config["path"] == "/test123"
    assert pkg(conf_path="/test_test").config["path"] == "/test_test"
    assert pkg(conf_path="/test-test").config["path"] == "/test-test"


def test_path_invalid(pkg):
    with pytest.raises(InvalidPackagePath):
        pkg(conf_path="test")

    with pytest.raises(InvalidPackagePath):
        pkg(conf_path="\\test")

    with pytest.raises(InvalidPackagePath):
        pkg(conf_path="\\test\\")

    with pytest.raises(InvalidPackagePath):
        pkg(conf_path="test/")

    with pytest.raises(InvalidPackagePath):
        pkg(conf_path="/test/")

    with pytest.raises(InvalidPackagePath):
        pkg(conf_path="/test.test")


def test_name_valid(pkg):
    len_name_str = "x" * 42

    assert pkg(name="test").meta["name"] == "test"
    assert pkg(name="test1_test2_test3").meta["name"] == "test1_test2_test3"
    assert pkg(name=len_name_str).meta["name"] == len_name_str


def test_name_invalid(pkg):
    with pytest.raises(InvalidPackageName):
        pkg(name="aioli")

    with pytest.raises(InvalidPackageName):
        pkg(name="aioli_core")

    with pytest.raises(InvalidPackageName):
        pkg(name="x" * 43)

    with pytest.raises(InvalidPackageName):
        pkg(name="test-test")

    with pytest.raises(InvalidPackageName):
        pkg(name="/test")

    with pytest.raises(InvalidPackageName):
        pkg(name="test^test")

    with pytest.raises(InvalidPackageName):
        pkg(name="test=test")

    with pytest.raises(InvalidPackageName):
        pkg(name="test/test")

    with pytest.raises(InvalidPackageName):
        pkg(name="test__")

    with pytest.raises(InvalidPackageName):
        pkg(name="__test")


def test_description_valid(pkg):
    text = "test_description"
    assert pkg(description=text).meta["description"] == text


def test_description_invalid(pkg):
    with pytest.raises(InvalidPackageDescription):
        pkg(description="a" * 257)
