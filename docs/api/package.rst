.. _package-docs:

Package
=======


The *Package* class is used for grouping and labeling a set of :ref:`Controllers <controller-docs>` and :ref:`Services <service-docs>`.
These components typically contain code that makes sense to modularize in the Application at hand.

Check out the :ref:`Extensions docs <extensions-docs>` to learn how Packages can be connected.


.. automodule:: aioli
.. autoclass:: Package
   :members:

Example – Creating a Package with Controller and Service layers

.. code-block:: python

    from aioli import Package

    from .service import VisitService, VisitorService
    from .controller import HttpController
    from .config import ConfigSchema


    export = Package(
        auto_meta=True,
        controllers=[HttpController],
        services=[VisitService, VisitorService],
        config=ConfigSchema,
    )


