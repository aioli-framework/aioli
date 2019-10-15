from functools import wraps

from starlette.requests import Request
from starlette.responses import Response

from aioli.exceptions import AioliException
from aioli.utils import jsonify

from .consts import Method, RequestProp
from .registry import Handler


def route(path, method, description=None):
    """Prepares route registration, and performs handler injection.

    :param path: Handler path, relative to application and unit paths
    :param method: HTTP Method
    :param description: Endpoint description
    :return: Route handler
    """

    def wrapper(fn):
        @wraps(fn)
        async def handler_fn(*args, **kwargs):
            return await fn(*args, **kwargs)

        if not isinstance(method, Method):
            raise AioliException(
                f"Invalid HTTP method supplied in @route for handler: {handler_fn}. "
                f"Must be of type: {Method.__module__}.{Method.__name__}"
            )

        handler = Handler(handler_fn)

        # Adds the handler for registration once the loop is ready.
        handler.register_route(path, method.value, description)

        return handler_fn

    return wrapper


def takes(props=None, **schemas):
    """Takes a list of schemas used to validate and transform parts of a request object.
    The selected parts are injected into the route handler as arguments.

    :param props: List of `Pluck` targets
    :param schemas: list of schemas (kwargs)
    :return: Route handler
    """

    header = schemas.get("header")
    body = schemas.get("body")
    path = schemas.get("path")
    query = schemas.get("query")

    def wrapper(fn):
        @wraps(fn)
        async def handler_fn(*args, **kwargs):
            args_new = list(args)
            request = kwargs["request"] if "request" in kwargs else args_new.pop(1)

            for prop in props or []:
                value = RequestProp(prop).value
                assert "." in value

                target = request

                for member in value.split("."):
                    target = getattr(target, member)

                kwargs.update({RequestProp(prop).name: target})

            if header:
                kwargs.update({"header": header().load(request.headers)})

            if path:
                kwargs.update(path().load(request.path_params))

            if body:
                payload = await request.json()
                kwargs.update({"body": body().load(payload)})

            if query:
                kwargs.update({"query": query().load(request.query_params)})

            return await fn(*args_new, **kwargs)

        handler = Handler(handler_fn)

        # Add the provided schemas to the RouteStack
        handler.schemas.from_dict(**schemas)

        return handler_fn

    return wrapper


def returns(schema_cls=None, status=200, many=False):
    """Returns a transformed and serialized Response

    :param schema_cls: Marshmallow.Schema class
    :param status: Return status (on success)
    :param many: Whether to return a list or single object
    :return: Response
    """

    schema = schema_cls(many=many) if schema_cls else None

    def wrapper(fn):
        @wraps(fn)
        async def handler_fn(unit, *args, **kwargs):
            args_new = list(args)

            # Remove `Request` object from args (in case it wasn't consumed by an `input_local`).
            if len(args) > 1 and isinstance(args[1], Request):
                args_new.pop(1)

            rv = await fn(unit, *args_new, **kwargs)

            indent = 4 if unit.app.config["pretty_json"] else 0

            if not schema:
                return jsonify(rv, status, indent=indent)

            data = (
                schema.dumps(rv, indent=indent, ensure_ascii=False).encode("utf8")
                if schema
                else rv
            )

            # Return HTTP encoded JSON response
            return Response(
                content=data,
                status_code=status,
                headers={"content-type": "application/json"},
            )

        handler = Handler(handler_fn)

        # Add the `response` schema to this handler
        handler.schemas.response = schema_cls
        handler.status = status

        return handler_fn

    return wrapper
