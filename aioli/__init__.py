from .exceptions import AioliException
from .package import Package
from .app import Application
from .datastores import FileStore

package_state = FileStore("packages", lifetime_secs=10)
