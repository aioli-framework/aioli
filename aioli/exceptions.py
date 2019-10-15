from starlette.exceptions import HTTPException


class CommandError(Exception):
    pass


class BootstrapError(Exception):
    pass


class UnitValidationError(BootstrapError):
    message = None

    def __init__(self, data, unit):
        self.unit = unit
        self.errors = data["messages"]


class UnitMetaError(UnitValidationError):
    def __init__(self, *args, unit, **kwargs):
        super(UnitMetaError, self).__init__(*args, unit, **kwargs)
        self.message = f"Unit {unit} failed metadata validation"


class UnitConfigError(UnitValidationError):
    def __init__(self, *args, unit, **kwargs):
        super(UnitConfigError, self).__init__(*args, unit, **kwargs)
        self.message = f"Unit {unit} failed configuration validation"


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
