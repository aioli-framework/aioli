from .root.commands import root_group, dev_start
from .pkg.commands import pkg_group

# Create CLI root
cli = root_group

# Add root commands
cli.add_command(dev_start)

# Add groups
cli.add_command(pkg_group)
