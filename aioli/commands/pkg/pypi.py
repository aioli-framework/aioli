import xmlrpc.client

from aioli import package_state


class Pypi(xmlrpc.client.ServerProxy):
    db_path = ".aioli"

    def __init__(self, *args, **kwargs):
        uri = kwargs.pop("uri", "https://pypi.org/pypi")
        super(Pypi, self).__init__(uri, *args, **kwargs)

    @property
    def packages(self):
        if package_state.age_seconds > 60:
            package_state["all"] = []
            query = dict(keywords=["aioli_package"])
            official = [pkg[1] for pkg in self.user_packages("aioli")]

            packages = []
            for result in self.search(query):
                name = result.get("name")
                pkg = name, result.get("summary"), result.get("version"), name in official
                packages.append(pkg)

            package_state["all"] = packages

        return package_state["all"]
