from aioli.service import BaseService


class ExampleService(BaseService):
    async def get_addr(self, request):
        return {"client": request.client}
