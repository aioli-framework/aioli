import asyncio

from geolite2 import geolite2

from aioli.service import BaseService
from aioli_rdbms import DatabaseService

from .. import database


class VisitorService(BaseService):
    geoip = geolite2.reader()
    db = None

    async def on_startup(self):
        """
        Integrates with the aioli_rdbms.DatabaseService when the Loop is available
        """

        self.db = self.integrate(DatabaseService).use_model(database.VisitorModel)

    async def get_one(self, visitor_id):
        """Return a single Visitor or raise an Exception

        :param visitor_id: Visitor ID
        :return: Single Visit
        """

        return await self.db.get_one(pk=visitor_id)

    async def get_many(self, **query):
        """Return a list of zero or more Visitors

        :param query: Visitor query parameters
        :return: List of Visitors
        """

        return await self.db.get_many(**query)

    async def ipaddr_location(self, remote_addr):
        """Resolve the given IP address' geographical location

        :param remote_addr: IP address
        :return: Geographical location (City, Country)
        """

        def in_english(*locations):
            for loc in locations:
                yield loc["names"]["en"]

        # Run the blocking geolite2 function in the executor
        loop = asyncio.get_running_loop()
        geoip = await loop.run_in_executor(None, self.geoip.get, remote_addr)

        if remote_addr in ["127.0.0.1", "::1"]:
            return "Localhost", "Localdomain"
        if not geoip:
            return "Unknown City", "Unknown Country"

        return in_english(geoip["city"], geoip["country"])
