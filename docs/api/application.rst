Application
===========

To run the Aioli application, an :class:`~aioli.Application` instance must be created.
Its constructor expects a *list* of at least one :class:`~aioli.Unit` to be registered with the application.


.. automodule:: aioli
   :noindex:
.. autoclass:: Application
   :inherited-members:
   :members: add_exception_handler


*Example – Guestbook Web API making use of the aioli_rdbms extension*

.. code-block:: python

    import aioli_guestbook
    import aioli_rdbms

    import toml

    from aioli import Application

    app = Application(
        config=toml.load("aioli.cfg"),
        units=[
            aioli_guestbook,
            aioli_rdbms,
        ]
    )

