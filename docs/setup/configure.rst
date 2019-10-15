.. _setup-configure-docs:

Configure
=========

The *Application* and associated *Units* can be configured using either environment variables,
or by a dictionary provided to the *config* parameter when creating the :class:`~aioli.Application`.


.. note::

    Note!

    :ref:`environment-config` takes precedence over :ref:`Application Constructor <constructor-config>` config.



Mappings
^^^^^^^^

Environment and Dictionary configs uses different naming conventions, for obvious reasons, but
follows the same logic.


Application
~~~~~~~~~~~

Mappings used for configuring core parts of an Aioli Application.

*Locations*

- Dictionary key: "aioli_core"
- Environment prefix: "AIOLI_CORE"
- Run-time access: :py:attr:`aioli.Application.config`

*Mappings*

.. table::
   :align: left

   ===================   =========================  ===========
   Dictionary            Environment                DEFAULT
   ===================   =========================  ===========
   dev_host              AIOLI_CORE_DEV_HOST        127.0.0.1
   dev_port              AIOLI_CORE_DEV_PORT        5000
   api_base              AIOLI_CORE_API_BASE        /api
   pretty_json           AIOLI_CORE_PRETTY_JSON     False
   allow_origins         AIOLI_CORE_ALLOW_ORIGINS   ["*"]
   debug                 AIOLI_CORE_DEBUG           False
   ===================   =========================  ===========


Unit
~~~~~~~

A custom *Unit* configuration schema can be defined using the :class:`~aioli.config.UnitConfigSchema` class,
which comes with a set of common parameters listed below.

*Locations*

- Dictionary key: [unit_name]
- Environment prefix: [PACKAGE_NAME]
- Run-time access: :py:attr:`aioli.Unit.config`

*Mappings*

.. table::
   :align: left

   ===================   ===================================  ===========
   Dictionary            Environment                          DEFAULT
   ===================   ===================================  ===========
   debug                 [PACKAGE_NAME]_DEBUG                 None
   controllers_enable    [PACKAGE_NAME]_CONTROLLERS_ENABLE    True
   services_enable       [PACKAGE_NAME]_SERVICES_ENABLE       True
   ===================   ===================================  ===========


Check out the :ref:`Unit Config Schema docs <unit-config-docs>` for info on how to extend the base schema
with custom parameters.


.. _environment-config:

Environment
^^^^^^^^^^^

Configuring Aioli using *Environment Variables* can be useful in some environments.

**Example**

.. code-block:: shell

   $ export AIOLI_CORE_DEV_HOST="0.0.0.0"
   $ export AIOLI_CORE_DEV_PORT="5555"
   $ export AIOLI_RDBMS_TYPE="mysql"
   $ export AIOLI_RDBMS_HOST="127.0.0.1"
   $ export AIOLI_RDBMS_DATABASE="aioli"
   $ export AIOLI_RDBMS_USERNAME="aioli"
   $ export AIOLI_RDBMS_PASSWORD="super_secret"
   $ export AIOLI_GUESTBOOK_VISITS_MAX="10"


.. _constructor-config:

Constructor
^^^^^^^^^^^

The configuration can be provided as a dictionary to the *config* parameter when creating the :class:`~aioli.Application`.

Check out an :ref:`Application configuration example <unit-config-schema-example>`.

Access
^^^^^^

Both :class:`~aioli.Application` and :class:`~aioli.Unit` configurations can be easily accessed from both :ref:`service-docs` and :ref:`controller-docs` instances,
using the `config` property.


