from .root import cli_root
from .pkg import cli_pkg

cli_root.add_command(cli_pkg)
