from aioli.controller import BaseHttpController, RequestProp, Method, schemas, route, takes, returns

from .service import VisitService, VisitorService
from .schema import Visit, Visitor, VisitorPath, VisitNew, VisitPath


class HttpController(BaseHttpController):
    def __init__(self, unit):
        super(HttpController, self).__init__(unit)
        self.visit = VisitService(unit)
        self.visitor = VisitorService(unit)

    async def on_request(self, request):
        self.log.debug(f"Request received: {request}")

    @route("/", Method.GET, "List of entries")
    @takes(query=schemas.HttpParams)
    @returns(Visit, many=True)
    async def visits_get(self, query):
        return await self.visit.get_many(**query)

    @route("/", Method.POST, "Create entry")
    @takes(body=VisitNew, props=[RequestProp.client_addr])
    @returns(Visit, status=201)
    async def visit_add(self, client_addr, body):
        return await self.visit.create(body, client_addr)

    @route("/{visit_id}", Method.GET, "Visit details")
    @takes(path=VisitPath)
    @returns(Visit)
    async def visit_get(self, visit_id):
        return await self.visit.get_one(visit_id)

    @route("/{visit_id}", Method.PUT, "Update entry")
    @takes(body=Visit, path=VisitPath, props=[RequestProp.client_addr])
    @returns(Visit)
    async def visit_update(self, visit_id, body, client_addr):
        return await self.visit.update(visit_id, body, client_addr)

    @route("/{visit_id}", Method.DELETE, "Delete entry")
    @takes(path=VisitPath, props=[RequestProp.client_addr])
    @returns(status=204)
    async def visit_delete(self, visit_id, client_addr):
        await self.visit.delete(visit_id, client_addr)

    @route("/visitors", Method.GET, "List of visitors")
    @takes(query=schemas.HttpParams)
    @returns(Visitor, many=True)
    async def visitors_get(self, query):
        return await self.visitor.get_many(**query)

    @route("/visitors/{visitor_id}", Method.GET, "Visitor details")
    @takes(path=VisitorPath)
    @returns(Visitor)
    async def visitor_get(self, visitor_id):
        return await self.visitor.get_one(visitor_id)

    @route("/visitors/{visitor_id}/visits", Method.GET, "Visits by visitor")
    @takes(path=VisitorPath, query=schemas.HttpParams)
    @returns(Visit)
    async def visitor_entries(self, visitor_id, query):
        query.update({"visitor": visitor_id})
        return await self.visit.get_many(**query)
