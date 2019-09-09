from aioli.controller import BaseHttpController, RequestProp, Method, schemas, route, takes, returns

from .service import ExampleService
from .schema import ExampleSchema


class HttpController(BaseHttpController):
    def __init__(self, pkg):
        super(HttpController, self).__init__(pkg)
        self.svc = ExampleService(pkg)

    @route("/", Method.GET)
    @returns(ExampleSchema)
    async def example(self, request):
        return await self.svc.get_addr(request)
