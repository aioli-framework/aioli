HTTP
====

Creating an HTTP Interface–be it RESTful or otherwise–is done using the
:class:`~aioli.controller.BaseHttpController` class.


*API*

.. automodule:: aioli.controller
.. autoclass:: BaseHttpController
   :members: on_startup, on_shutdown, on_request


*Example – Controller without route handlers*

.. code-block:: python

    from aioli.controller import BaseHttpController

    from .service import VisitService


    class HttpController(BaseHttpController):
        def __init__(self):
            super(HttpController, self).__init__(unit)

            self.log.debug("Guestbook opening")
            self.visit = VisitService(unit)

        async def on_startup(self):
            self.log.debug(f"Guestbook opened")

        async def on_request(self, request):
            self.log.debug(f"Request received: {request}")


Route
-----

Route handlers are standard Python methods decorated with `@route`.

*API*

.. automodule:: aioli.controller.decorators
   :members: route

*Example – Route handler without transformation helpers*

.. code-block:: python

    from aioli.controller import BaseHttpController, Method, route

    from .service import VisitService


    class Controller(BaseController):
        def __init__(self):
            self.visit = VisitService()

        @route("/", Method.GET, "List of entries")
        async def visits_get(self, request):
            # Pass along the query params as-is.
            # Then..
            # Return whatever get_many() returned.
            return await self.visit.get_many(**query)

Transform
---------

Transformation is implemented on route handlers using `@takes` and `@returns`. These decorators offer
a simple yet powerful way of shaping and validating request data, while also ensuring API endpoints
returns according to their schemas.

Takes
~~~~~

The `@takes` decorator is used to instruct Aioli how to deserialize and validate parts of a request,
and injects the validated data as arguments into the decorated function.

*API*

.. automodule:: aioli.controller.decorators
   :noindex:
   :members: takes

*Example – Route handler making use of @takes*

.. code-block:: python

    from aioli.controller import (
        BaseHttpController, ParamsSchema, RequestProp,
        Method, route, takes
    )

    from .service import VisitService


    class Controller(BaseController):
        def __init__(self):
            self.visit = VisitService()

        @route("/", Method.GET, "List of entries")
        @takes(query=ParamsSchema)
        async def visits_get(self, query):
            # Transform and validate query params using
            # ParamsSchema and pass along to get_many().
            # Then..
            # Return whatever get_many() returned.
            return await self.visit.get_many(**query)



Returns
~~~~~~~

The `@returns` decorator takes care of serializing data returned by its route handler, into JSON.

*API*

.. automodule:: aioli.controller.decorators
   :noindex:
   :members: returns


*Example – Route handler making use of @takes and @returns*

.. code-block:: python

    from aioli.controller import (
        BaseHttpController, ParamsSchema, RequestProp,
        Method, route, takes, returns
    )

    from .service import VisitService


    class Controller(BaseController):
        def __init__(self):
            self.visit = VisitService()

        @route("/", Method.GET, "List of entries")
        @takes(query=ParamsSchema)
        @returns(Visit, many=True)
        async def visits_get(self, query):
            # Transform and validate query params using
            # ParamsSchema and pass along to VisitService.get_many()
            # Then..
            # Transform and dump the object returned by get_many()
            # using the Visit schema, as a JSON encoded response.
            return await self.visit.get_many(**query)
