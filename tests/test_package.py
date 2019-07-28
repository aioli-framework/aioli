import pytest

from aioli.controller import BaseHttpController, BaseWebSocketController
from aioli.service import BaseService
from aioli.config import PackageConfigSchema


from aioli.exceptions import (
    BootstrapException,
    InvalidPackageName,
    InvalidPackageVersion,
    InvalidPackagePath
)


def test_configschema_valid(pkg):
    class Config(PackageConfigSchema):
        pass

    assert pkg().conf_schema == PackageConfigSchema
    assert pkg(config=None).conf_schema == PackageConfigSchema
    assert pkg(config=Config).conf_schema == Config


def test_configschema_invalid(pkg):
    with pytest.raises(BootstrapException):
        pkg(config=False)

    with pytest.raises(BootstrapException):
        pkg(config={"test": "test"})

    with pytest.raises(BootstrapException):
        pkg(config=[])

    with pytest.raises(BootstrapException):
        pkg(config=[Exception])


def test_services_valid(pkg):
    class Service1(BaseService):
        pass

    class Service2(BaseService):
        pass

    assert Service1 in pkg(services=[Service1])._services
    assert Service2 in pkg(services=[Service2])._services

    multi = pkg(services=[Service1, Service2])._services
    assert Service1 in multi
    assert Service2 in multi

    assert pkg(services=[])._services == set()
    assert pkg(services=None)._services == set()


def test_services_invalid(pkg):
    with pytest.raises(BootstrapException):
        pkg(services=False)

    with pytest.raises(BootstrapException):
        pkg(services={"test": "test"})

    with pytest.raises(BootstrapException):
        pkg(services=set())

    with pytest.raises(BootstrapException):
        pkg(services=[Exception])


def test_controllers_valid(pkg):
    class HttpController1(BaseHttpController):
        pass

    class HttpController2(BaseHttpController):
        pass

    class WebSocketController(BaseWebSocketController):
        pass

    assert HttpController1 in pkg(controllers=[HttpController1])._controllers
    assert HttpController2 not in pkg(controllers=[HttpController1])._controllers

    multi = pkg(controllers=[HttpController1, HttpController2, WebSocketController])._controllers
    assert HttpController1 in multi
    assert HttpController2 in multi
    assert WebSocketController in multi

    assert pkg(controllers=[])._controllers == set()
    assert pkg(controllers=None)._controllers == set()


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
    assert pkg(version="0.0.0").version == "0.0.0"
    assert pkg(version="1.2.3").version == "1.2.3"
    assert pkg(version="11.905.67").version == "11.905.67"
    assert pkg(version="2.0.3-beta.0").version == "2.0.3-beta.0"
    assert pkg(version="2.0.3-pre-alpha.1.2").version == "2.0.3-pre-alpha.1.2"
    assert pkg(version="2.0.3+b.1056").version == "2.0.3+b.1056"
    assert pkg(version="2.0.3-pre-alpha.1.2+b.1056").version == "2.0.3-pre-alpha.1.2+b.1056"


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


def test_path_valid(pkg_registered):
    assert pkg_registered("/test").path == "/test"
    assert pkg_registered("/test123").path == "/test123"
    assert pkg_registered("/test_test").path == "/test_test"
    assert pkg_registered("/test-test").path == "/test-test"


def test_path_invalid(pkg_registered):
    with pytest.raises(InvalidPackagePath):
        pkg_registered("test")

    with pytest.raises(InvalidPackagePath):
        pkg_registered("\\test")

    with pytest.raises(InvalidPackagePath):
        pkg_registered("\\test\\")

    with pytest.raises(InvalidPackagePath):
        pkg_registered("test/")

    with pytest.raises(InvalidPackagePath):
        pkg_registered("/test/")

    with pytest.raises(InvalidPackagePath):
        pkg_registered("/test.test")


def test_name_valid(pkg):
    len_name_str = "x" * 42

    assert pkg(name="test").name == "test"
    assert pkg(name="test1_test2_test3").name == "test1_test2_test3"
    assert pkg(name=len_name_str).name == len_name_str


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
    text = "TestTest12"
    assert pkg(description=text).description == text


def test_description_invalid(pkg):
    with pytest.raises(BootstrapException):
        assert pkg(description="a" * 257)
