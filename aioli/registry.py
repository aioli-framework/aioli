import os
import logging
import configparser

from enum import Enum

from importlib_metadata import metadata
from marshmallow.exceptions import ValidationError

from .exceptions import (
    BootstrapError,
    UnitMetaError,
    UnitConfigError
)

from .unit import Unit, UnitMetadata


class ComponentType(Enum):
    services = "service"
    controllers = "controller"


class UnitConfig:
    def __init__(self, name, data, schema):
        self.name = name

        try:
            self._data = schema(name).load(data)
        except ValidationError as e:
            raise UnitConfigError(e.__dict__, unit=name)

    def get(self, item, fallback):
        return self._data.get(item) or fallback

    def __getitem__(self, item):
        return self._data[item]

    def __setitem__(self, key, value):
        self._data[key] = value


class ImportRegistry:
    imported = []
    log = logging.getLogger("aioli.unit")

    def __init__(self, app, config):
        self._config = config
        self._app = app

    def declare_unit(self, unit):
        if unit not in self.imported:
            self.imported.append(unit)

    def get_import(self, name):
        for imported in self.imported:
            if name == imported.name:
                return imported

        raise RuntimeError(f"Unit {name} is not attached to this application")

    def get_config(self, module_name, schema_cls):
        unit_name = module_name.replace("_", "-")
        data = self._config.get(unit_name, {})
        return UnitConfig(unit_name, data, schema_cls)

    def register_units(self, registerables):
        registerables = set(registerables)

        for registerable in registerables:
            unit = registerable.export if hasattr(registerable, "export") else registerable

            if not isinstance(unit, Unit):
                raise BootstrapError(
                    f"Expected an Aioli-type Python Unit, or an aioli.Unit, got: {registerable}"
                )

            meta = None

            if unit._auto_meta and hasattr(registerable, "__path__"):
                pyproject_file = "pyproject.toml"
                self.log.debug(f"Looking for project metadata [auto_meta]")
                pyproject_path = os.path.join(registerable.__path__[0], "..", pyproject_file)

                if os.path.exists(pyproject_path):  # Meta from pyproject
                    parser = configparser.ConfigParser()
                    parser.read(pyproject_path)
                    pyproject = parser["tool.poetry"]
                    meta = {k: v.strip('"') for k, v in pyproject.items() if k in ["name", "description", "version"]}
                elif hasattr(registerable, "__name__"):  # Meta from dist
                    dist = dict(metadata(registerable.__name__))
                    meta = dict(
                        name=dist.get("Name"),
                        version=dist.get("Version"),
                        description=dist.get("Summary")
                    )
            elif unit._meta:
                meta = unit._meta
            else:
                raise BootstrapError(f"Unable to locate metadata for {registerable}")

            try:
                unit.meta = UnitMetadata().load(meta)
                self.log.info("Attaching {name}/{version}".format(**unit.meta))
                unit.register(self._app)
            except ValidationError as e:
                raise UnitMetaError(e.__dict__, unit=registerable)

            self.declare_unit(unit)

    async def call_startup_handlers(self):
        total = failed = 0

        for unit in self.imported:
            total += 1

            try:
                await unit.call_startup_handlers()
            except Exception:
                failed += 1
                unit_name = unit.meta['name']
                self.log.exception(f"When calling startup hooks for {unit_name}:")

        return total, failed
