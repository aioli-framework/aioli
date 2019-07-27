from starlette.exceptions import HTTPException


class BootstrapException(Exception):
    pass


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
