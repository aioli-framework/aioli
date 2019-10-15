.. _extensions-docs:

Info
====

An Extension is comprised of one or more Services deriving from :class:`~aioli.service.BaseService` and typically
creates an abstraction layer for accessing a remote system. Furthermore, this type of *Unit* usually implements the
`Factory pattern <https://en.wikipedia.org/wiki/Factory_method_pattern>`_.

Check out the `aioli-rdbms extension <https://github.com/aioli-framework/aioli-rdbms>`_ for an example.


Import
======

To make use of an Extension, its Unit along with dependencies needs to be registered with the Application.

Once registered, the Extension's Service(s) can be incorporated into other *Units* using
:meth:`~aioli.service.BaseService.integrate` or :meth:`~aioli.service.BaseService.connect`.

**Example**

Register the local *users* Unit and its dependency; *aioli_rdbms*.

.. code-block:: python

   import aioli_rdbms

   import toml

   from aioli import Application

   import .users

   app = Application(
       config=toml.load("aioli.cfg"),
       packages=[users, aioli_rdbms]
   )




The *aioli_rdbms.Service* can now be attached to *users.UsersService*:

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


Publish
=======

Shortly, a Unit Management CLI will be added, along with the
`https://pkgs.aioli.dev <https://pkgs.aioli.dev>`_ website for showing useful info about extension-type *Units*;
their trust status, install instructions, author and license data, as well as links to source code and more.
