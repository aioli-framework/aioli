from starlette.exceptions import HTTPException


class CommandError(Exception):
    pass


class BootstrapError(Exception):
    pass


class PackageValidationError(BootstrapError):
    message = None

    def __init__(self, data, package):
        self.package = package
        self.errors = data["messages"]


class PackageMetaError(PackageValidationError):
    def __init__(self, *args, package, **kwargs):
        super(PackageMetaError, self).__init__(*args, package, **kwargs)
        self.message = f"Package {package} failed metadata validation"


class PackageConfigError(PackageValidationError):
    def __init__(self, *args, package, **kwargs):
        super(PackageConfigError, self).__init__(*args, package, **kwargs)
        self.message = f"Package {package} failed configuration validation"


class AioliException(HTTPException):
    def __init__(self, status=500, message="Internal Server Error"):
        super(AioliException, self).__init__(status_code=status, detail=message)


class InvalidChannelError(HTTPException):
    def __init__(self):
        super(InvalidChannelError, self).__init__(
            status_code=400, detail="Invalid channel provided"
        )


class DatabaseError(HTTPException):
    def __init__(self):
        super(DatabaseError, self).__init__(status_code=500, detail="Database error")


class NoMatchFound(HTTPException):
    def __init__(self, message="Not Found"):
        super(NoMatchFound, self).__init__(status_code=404, detail=message)
