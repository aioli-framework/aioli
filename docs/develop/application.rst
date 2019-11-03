Application
===========

The :class:`~aioli.Application` constructor expects one or more :class:`~aioli.Unit` modules to be registered with the instance.

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

