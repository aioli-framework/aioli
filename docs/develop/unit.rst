.. _unit-docs:

Unit
====

For code to be allowed registration with an Application–be it a local package, an extension or something else–it must
adhere to the Aioli *Unit* format, which mainly serves the purpose of providing modularity, consistency and flexibility.

Units, in its simplest form, are tagged groups of one or more *Components* in the form of:

- Services: Implements application logic and exposes an API for internal consumption
- Controllers: Handles HTTP requests and typically interacts with *Service* APIs


.. automodule:: aioli
.. autoclass:: Unit
   :members:

Example – Creating a Unit with Controller and Service layers

.. code-block:: python

    from aioli import Unit

    from .service import VisitService, VisitorService
    from .controller import HttpController
    from .config import ConfigSchema


    export = Unit(
        auto_meta=True,
        controllers=[HttpController],
        services=[VisitService, VisitorService],
        config=ConfigSchema,
    )


.. _extensions-docs:

Extend
------

:ref:`Units <unit-docs>` can be connected using :meth:`~aioli.service.BaseService.integrate` or :meth:`~aioli.service.BaseService.connect`,
and those with the sole purpose of serving others, are known as *Extensions*.

Example – Leverage the `aioli-rdbms <https://github.com/aioli-framework/aioli-rdbms>`_ Unit to gain database access

.. code-block:: python

    from aioli import BaseService
    from aioli_rdbms import DatabaseService

    from .database import UserModel

    class UsersService(BaseService):
        db = None

        async def on_startup(self):
            self.db = (
                self.integrate(DatabaseService)
                .use_model(UserModel)
            )

        async def get_one(user_id):
            return await self.db.get_one(pk=user_id)

        ...


