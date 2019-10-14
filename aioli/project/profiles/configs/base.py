from abc import ABC, abstractmethod


class ProfileConfig(ABC):
    def __init__(self, overrides=None):
        for prop, value in overrides or []:
            if not getattr(self, prop):
                raise KeyError(f"No such template attribute: {prop}")

            setattr(self, prop, value)

    @property
    @abstractmethod
    def app_dir(self):
        pass

    @property
    @abstractmethod
    def export_obj(self):
        pass

    @property
    @abstractmethod
    def http_api(self):
        pass

    @property
    @abstractmethod
    def metadata(self):
        pass

    @property
    @abstractmethod
    def appconfig(self):
        pass
