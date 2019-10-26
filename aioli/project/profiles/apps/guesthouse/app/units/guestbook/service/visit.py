from aioli.service import BaseService
from aioli.exceptions import AioliException, NoMatchFound

from aioli_rdbms import DatabaseService

from .visitor import VisitorService

from .. import database


class VisitService(BaseService):
    visitor: VisitorService
    db = None

    async def on_startup(self):
        """
        Integrates with the aioli_rdbms.DatabaseService and connects the VisitorService when the Loop is available
        """

        self.db = self.integrate(DatabaseService).use_model(database.VisitModel)
        self.visitor = self.connect(VisitorService)

    @staticmethod
    def raise_if_unauthorized(visit, remote_addr):
        """
        Convenience function for raising an exception if the given address doesn't
        match the Visit's address.

        :param visit: Visit object
        :param remote_addr: Visitor TCP address
        """

        if visit.visitor.ip_addr != remote_addr:
            raise AioliException(status=403, message="Not allowed from this IP")

    async def get_one(self, visit_id):
        """Return a single Visit or raise an Exception

        :param visit_id: Visit ID
        :return: Single Visit
        """

        return await self.db.get_one(pk=visit_id)

    async def get_many(self, **query):
        """Return a list of zero or more Visits

        :param query: Visit query parameters
        :return: List of Visits
        """

        return await self.db.get_many(**query)

    async def delete(self, visit_id, remote_addr):
        """Deletes a Visit using id after ensuring addresses matches

        :param visit_id: Visit ID
        :param remote_addr: Visitor TCP address
        """

        visit = await self.db.get_one(pk=visit_id)
        self.raise_if_unauthorized(visit, remote_addr)
        return await visit.delete()

    async def update(self, visit_id, payload, remote_addr):
        """Updates a Visit using id after ensuring addresses matches

        :param visit_id: Visit ID
        :param payload: Update payload
        :param remote_addr: Visitor TCP address
        :return: The updated record
        """

        visit = await self.db.get_one(pk=visit_id)
        self.raise_if_unauthorized(visit, remote_addr)
        return await self.db.update(visit, payload)

    async def create(self, visit, remote_addr):
        """Register new visit

        :param visit: Information about the visit
        :param remote_addr: Visitor TCP address
        :return: The created record
        """

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
