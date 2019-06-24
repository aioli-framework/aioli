.. _package-config-schema-example:


Package config schema
=====================

This example uses code from the `aioli_rdbms <https://github.com/aioli-framework/aioli-rdbms>`_ extension Package.


Create
^^^^^^

Define a custom Package configuration schema.

*File: aioli_rdbms/config.py*

.. code-block:: python

   from aioli.config import PackageConfigSchema, fields, validate


   class ConfigSchema(PackageConfigSchema):
       type = fields.String(
           validate=validate.OneOf(["mysql", "postgres"]),
           required=True
       )
       username = fields.String(required=True)
       password = fields.String(required=True)
       host = fields.String(missing="127.0.0.1")
       port = fields.Integer(missing=3306)
       database = fields.String(missing="aioli")


Associate
^^^^^^^^^

Associate the configuration schema with a Package.

*File: aioli_rdbms/__init__.py*

.. code-block:: python

    from aioli import Package

    from .service import DatabaseService
    from .config import ConfigSchema


    export = Package(
        name="aioli_rdbms",
        version="0.1.0",
        description="ORM and CRUD Service for Aioli with support for MySQL and PostgreSQL",
        controllers=[],
        services=[DatabaseService],
        config=ConfigSchema,
    )


Configure
^^^^^^^^^

Create the configuration using the format of choice.

*File: config.toml*

.. code-block:: toml

   [aioli_core]
   dev_port = 5555
   path = "/api"
   debug = true

   [aioli_guestbook]
   path = "/guestbook"
   # Maximum number of visits per IP
   visits_max = 14

   [aioli_rdbms]
   type = "(mysql|postgres)"
   username = "user"
   password = "pass"
   host = "127.0.0.1"
   port = 3306
   database = "aioli"

Register
^^^^^^^^

Parse the configuration file and pass it as a Dictionary to the :class:`~aioli.Application` constructor.

*File: my_application/main.py*

.. code-block:: python

   import aioli_guestbook
   import aioli_rdbms

   import toml

   from aioli import Application

   app = Application(
       config=toml.load("config.toml"),
       packages=[
           aioli_guestbook,
           aioli_rdbms,
       ]
   )

