.. _service-to-service-example:


Connecting Services
===================

Service making use of other services with `integrate` and `connect`.

.. code-block:: python

    from aioli.service import BaseService
    from aioli.exceptions import AioliException, NoMatchFound

    from aioli_rdbms import DatabaseService

    from .visitor import VisitorService

    from .. import database


    class VisitService(BaseService):
        visitor: VisitorService
        db = None

        async def on_startup(self):
            self.db = self.integrate(DatabaseService).use_model(database.VisitModel)
            self.visitor = self.connect(VisitorService)

        async def get_authored(self, visit_id, remote_addr):
            visit = await self.db.get_one(pk=visit_id)
            if visit.visitor.ip_addr != remote_addr:
                raise AioliException(status=403, message="Not allowed from your IP")

            return visit

        async def delete(self, visit_id, remote_addr):
            visit = await self.get_authored(visit_id, remote_addr)
            await visit.delete()

        async def update(self, visit_id, payload, remote_addr):
            visit = await self.get_authored(visit_id, remote_addr)
            return await self.db.update(visit, payload)

        async def create(self, remote_addr, visit):
            visit_count = await self.db.count(visitor__ip_addr__iexact=remote_addr)
            visits_max = self.config["visits_max"]

            if visit_count >= visits_max:
                raise AioliException(
                    status=400,
                    message=f"Max {visits_max} entries per IP. Try deleting some old ones.",
                )

            async with self.db.manager.database.transaction():
                city, country = await self.visitor.ipaddr_location(remote_addr)

                visitor = dict(
                    name=visit.pop("visitor_name"),
                    ip_addr=remote_addr,
                    location=f"{city}, {country}",
                )

                try:
                    visit["visitor"] = await self.visitor.db.get_one(**visitor)
                except NoMatchFound:
                    visit["visitor"] = await self.visitor.db.create(**visitor)
                    self.unit.log.info(f"New visitor: {visit['visitor'].name}")

                visit_new = await self.db.create(**visit)
                self.log.info(f"New visit: {visit_new.id}")

            return await self.db.get_one(pk=visit_new.id)
