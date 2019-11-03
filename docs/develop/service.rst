.. _service-docs:

Service
=======

The typical *Service Component* takes care of interacting with external systems: Databases, Remote Web APIs, Messaging systems, etc. and
provides an API for internal consumption.

Check out the :ref:`service-to-service-example` example to see how a service can integrate and interact with other services.

.. automodule:: aioli.service
.. autoclass:: BaseService
   :members: on_startup, on_shutdown, integrate, connect
