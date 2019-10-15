import importlib

from os import mkdir
from pathlib import Path
from distutils import dir_util

from . import writers


class Template:
    def __init__(self, app_unit, template_mod, template_cls):
        self.mod = importlib.import_module(template_mod)
        self.params = getattr(self.mod, template_cls)()
        self.app_unit = importlib.import_module(app_unit)
        self.abspath = self.app_unit.__path__[0]


TEMPLATES = dict(
    basic=Template(
        "aioli.project.profiles.apps.basic",
        "aioli.project.profiles.configs.basic",
        "BasicProfileConfig"
    )
)


class TemplateInstaller:
    def __init__(self, name, template_name="basic", parent_dir=".", metadata=True, appconfig=True, app_dir=None):
        self.parent_dir = parent_dir
        self.name = name
        self.abspath = str(Path(f"{parent_dir}/{name}").absolute())
        self.enable_metadata = metadata
        self.enable_appconfig = appconfig
        self.template = TEMPLATES[template_name]
        self.app_dir = app_dir or self.template.params.app_dir

    def write_base(self):
        if Path(self.abspath).exists():
            raise ValueError(f"Error: Target directory {self.abspath} already exists")

        tmpl = self.template

        # Create root path
        mkdir(self.abspath)

        objects = []

        # Create app path
        for abspath in dir_util.copy_tree(f"{tmpl.abspath}/app", f"{self.abspath}/{self.app_dir}"):
            relpath = str(Path(abspath).relative_to(self.abspath))
            objects.append(relpath)

        if self.enable_metadata:
            writers.poetry_config(
                f"{self.abspath}/{self.template.params.metadata}",
                data=dict(
                    core={"name": self.name},
                    dependencies={"python": "^3.6"},
                    build_system={}
                )
            )

            objects.append(self.template.params.metadata)

        if self.enable_appconfig:
            writers.appconfig(
                f"{self.abspath}/{self.template.params.appconfig}",
                core=dict(
                    api_base=self.template.params.http_api
                ),
                extra=[
                    ("unit-example", {"path": "/whoami"})
                ]
            )

            objects.append(self.template.params.appconfig)

        return dict(
            path=self.abspath,
            export=f"{tmpl.params.app_dir}:{tmpl.params.export_obj}",
            files=objects,
            interfaces={
                "http": tmpl.params.http_api,
            }
        )
