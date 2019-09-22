from .exceptions import AioliException
from .package import Package
from .app import Application
from .datastores import FileStore
from .cli.config import PYPI_LIFETIME_SECS

package_state = FileStore("packages", lifetime_secs=PYPI_LIFETIME_SECS)
