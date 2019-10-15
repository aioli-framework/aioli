from .root import cli_root
from .repositories import cli_unit

cli_root.add_command(cli_unit)
