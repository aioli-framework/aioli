CLI
===

The *Aioli CLI* provides a set of commands for managing an Aioli project.


attach
------

Attaches the given application instance.

*Example – attach app at my_app:export*

.. code-block:: shell

   $ aioli --app_path my_app:export attach


info
----
Dump details about the current application.

*Example – dump info about my_app:export*

.. code-block:: shell

   $ aioli info


create
------

Create a new app with the given name.

*Command input*

.. table::
   :align: left

   ===================   ==================   =================
   Name                  Default              Description
   ===================   ==================   =================
   --dst_path            Current directory    Directory in which to create the project
   --profile             minimal              One of: minimal, guesthouse, whoami
   --confirm             Not set              Answer yes to confirmations
   ===================   ==================   =================



*Example – create a new app using the guesthouse profile*

.. code-block:: shell

   $ aioli create beachhouse --profile guesthouse


start
-----

Starts a development server.

.. table::
   :align: left

   ===================   ==================   ========================
   Name                  Default              Description
   ===================   ==================   ========================
   --host                127.0.0.1            Bind socket to this host
   --port                5000                 Bind socket to this port
   --no_reload           Not set              Disable the reloader
   --no_debug            Not set              Disable debug mode
   --workers             1                    Number of workers
   ===================   ==================   ========================


*Example – Start the attached application on port 127.0.0.1:1234*

.. code-block:: shell

   $ aioli start --port 1234


units
-----

Show a info about attached or remotely available (PyPI) Aioli units.

local
^^^^^

Work with local units.

*Example – show a list of local Units*

.. code-block:: shell

    $ aioli units local list

pypi
^^^^

Work with Units on PyPI.

*Example – show details about the aioli-openapi Unit on PyPI*

.. code-block:: shell

    $ aioli units pypi show aioli-openapi
