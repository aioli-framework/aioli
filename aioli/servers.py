from uvicorn.importer import import_from_string
from uvicorn.main import Server
from uvicorn.config import Config
from uvicorn.supervisors import Multiprocess, StatReload

from aioli.log import setup_logging


class UvicornServer(Server):
    def __init__(self, app_path, *args, **kwargs):
        super(UvicornServer, self).__init__(*args, **kwargs)
        self.app_path = app_path

    def run(self, *args, **kwargs):
        app = import_from_string(self.app_path)
        setup_logging(level=self.config.log_level.upper())
        app.load_units()

        super().run(*args, **kwargs)


def uvicorn_server(app_path, **kwargs):
    config = Config(app_path, **kwargs)
    setup_logging(level=config.log_level.upper())
    server = UvicornServer(app_path, config=config)

    if config.reload and not isinstance(app_path, str):
        config.logger_instance.warn(
            "auto-reload only works when app is passed as an import string."
        )

    if isinstance(app_path, str) and (config.debug or config.reload):
        socket = config.bind_socket()
        supervisor = StatReload(config)
        supervisor.run(server.run, sockets=[socket])
    elif config.workers > 1:
        socket = config.bind_socket()
        supervisor = Multiprocess(config)
        supervisor.run(server.run, sockets=[socket])
    else:
        server.run()
