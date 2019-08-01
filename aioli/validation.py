import re

from .exceptions import (
    InvalidPackagePath,
    InvalidPackageName,
    InvalidPackageVersion,
    InvalidPackageDescription
)

# Reserved Package names
NAMES_RESERVED = ["aioli", "aioli_core"]

# Allowed Package name format
NAME_REGEX = re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)*$")

# Semantic version regex
# 1 - Major
# 2 - Minor
# 3 - Patch
# 4 (optional) - Pre-release version info
# 5 (optional) - Metadata (build time, number, etc.)
VERSION_REGEX = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(-[a-zA-Z\d][-a-zA-Z.\d]*)?(\+[a-zA-Z\d][-a-zA-Z.\d]*)?$"
)


# Allowed Package path format
PATH_REGEX = re.compile(r"^/[a-zA-Z0-9-_]*$")


def validate_path(value):
    if not PATH_REGEX.match(value):
        raise InvalidPackagePath(f"Path {value} contains invalid characters")

    return value


def validate_version(value):
    if not VERSION_REGEX.match(value):
        raise InvalidPackageVersion(f"Version {value} is invalid, must be Semantic Versioning string")

    return value


def validate_name(value):
    if value in ["aioli", "aioli_core"]:
        raise InvalidPackageName(f"Name {value} is reserved and cannot be used")
    elif not NAME_REGEX.match(value) or len(value) > 42:
        raise InvalidPackageName(f"Name {value} is invalid. It may contain up to "
                                 f"42 lowercase alphanumeric and underscore characters.")

    return value


def validate_description(value):
    if len(value) > 256:
        raise InvalidPackageDescription(f"Description {value} is invalid, can be at most 256 characters long")

    return value
