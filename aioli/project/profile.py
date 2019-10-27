import importlib
from .profiles import configs


class TemplateProfile:
    def __init__(self, app_unit, config_cls):
        self.params = getattr(configs, config_cls)()
        self.app_unit = importlib.import_module(app_unit)
        self.abspath = self.app_unit.__path__[0]


TEMPLATE_PROFILES = dict(
    minimal=TemplateProfile(
        "aioli.project.profiles.apps.minimal",
        "StandardConfig"
    ),
    guesthouse=TemplateProfile(
        "aioli.project.profiles.apps.guesthouse",
        "GuesthouseConfig"
    ),
    whoami=TemplateProfile(
        "aioli.project.profiles.apps.whoami",
        "StandardConfig"
    )
)
