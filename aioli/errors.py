from .utils import jsonify


async def server_error(_, exc):
    if isinstance(exc, NotImplementedError):
        message = "Not implemented"
    else:
        message = "Internal server error"

    return jsonify({"message": message}, status=500)


async def validation_error(_, exc):
    return jsonify({"message": exc.messages}, status=422)


async def decode_error(*_):
    return jsonify({"message": "Error decoding JSON"}, status=400)


async def http_error(_, exc):
    return jsonify({"message": exc.detail}, status=exc.status_code)

