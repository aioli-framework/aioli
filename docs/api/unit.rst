.. _package-docs:

Unit
=======


The *Unit* class is used for grouping and labeling a set of :ref:`Controllers <controller-docs>` and :ref:`Services <service-docs>`.
These components typically contain code that makes sense to modularize in the Application at hand.

Check out the :ref:`Extensions docs <extensions-docs>` to learn how Units can be connected.


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


