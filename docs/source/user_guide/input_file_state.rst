.. _input_file_state:

State file
==========

The *state file* must be located in **state** directory (see see :ref:`project_dir`). A state file defines one or more aerodynamic states which are to be analysed. A simple example for a state file is shown below.

.. include:: pytornado/state/template.json
    :code: json

Flight state keywords
---------------------

* ``airspeed`` True airspeed (TAS) of the aircraft in *meter per second*
* ``alpha`` Angle of attack in *degrees*
* ``altitude`` Flight altitude as geometric height in *meters*
* ``beta`` Side slip angles in *degrees*
* ``density`` Air density in *kilogram per meter^3*
* ``mach`` Flight Mach number
* ``rate_P`` Aircraft rotation rate about the body-fixed *X-axis* in *radians per seconds*
* ``rate_Q`` Aircraft rotation rate about the body-fixed *Y-axis* in *radians per seconds*
* ``rate_R`` Aircraft rotation rate about the body-fixed *Z-axis* in *radians per seconds*

The aerodynamic angles *alpha* and *beta* are measured relative to the body-fixed system 

|Apms|
------

|name| can perform batch analyses and create a so-called |apm|. In order to analyse multiple flight states, you can create a list of values for each flight state keyword (instead of using single numerical values). An example state file for an |apm| analysis is shown below.

.. include:: state_apm_example.json
    :code: json

In this example *three* separate flight states are computed, and for each analysis results can be saved separately. It is important that every list has an equal number of items. The first item of every list defines the flight state, the second item of every list defines the second flight state, etc. Notice that the flight state can be defined by any valid combination of ``airspeed``, ``altitude``, ``mach`` and ``density``. Valid combinations are:

* ``airspeed`` and ``density``
* ``airspeed`` and ``altitude``
* ``mach`` and ``altitude``

For instance, if ``airspeed`` and ``density`` are used, ``mach`` and ``altitude`` can be omitted, or set to ``null``.

.. hint::

    Internally, |name| will run all computations using the *airspeed* and the *air density*. If you choose ``altitude`` as input, |name| will compute the *air density* and the *speed of sound*. |name| uses the `ICAO Standard Atmosphere 1993 <https://github.com/aarondettmann/ambiance>`_ as the atmospheric model.

CPACS |Apms|
------------

|Apms| defined in CPACS_ can also be evaluated using |name|. How to load CPACS_ defined |apms| is described here:

   * :ref:`input_file_cpacs`
