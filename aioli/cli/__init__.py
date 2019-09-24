import os
import sys

from .commands import cli_root
from . import config, utils


def run():
    # The `aioli` cli script, created by Poetry using pkg_resources,
    # appears to set the WD to whatever directory the caller comes from (@TODO needs verification).
    # In our case, this is the Aioli Framework, and not the actual CWD.
    # Fix: This will add the actual CWD to PATH before invoking the CLI.
    sys.path.append(os.getcwd())

    return cli_root(prog_name='aioli')
