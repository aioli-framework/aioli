from aioli.controller import BaseHttpController, RequestProp, Method, schemas, route, takes, returns

from .service import ExampleService
from .schema import ExampleSchema


class HttpController(BaseHttpController):
    def __init__(self, unit):
        super(HttpController, self).__init__(unit)
        self.svc = ExampleService(unit)

    @route("/", Method.GET)
    @returns(ExampleSchema)
    async def example(self, request):
        return await self.svc.get_addr(request)
