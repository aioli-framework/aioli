import importlib


class TemplateProfile:
    def __init__(self, app_unit, template_mod, template_cls):
        self.mod = importlib.import_module(template_mod)
        self.params = getattr(self.mod, template_cls)()
        self.app_unit = importlib.import_module(app_unit)
        self.abspath = self.app_unit.__path__[0]


PROFILES = dict(
    standard=TemplateProfile(
        "aioli.project.profiles.apps.standard",
        "aioli.project.profiles.configs.standard",
        "StandardProfileConfig"
    )
)


def get_profile(name):
    return PROFILES[name]
