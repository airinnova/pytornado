General remarks
===============

.. hint::

    This part of the documentation is intended to give additional information for someone who would like to develop the |name| code. Notice that the user guide is found here: :ref:`detailed_user_guide`.

Programming languages
---------------------

* |name| is written in Python and C++
* All Python code is compatible with version >=3.6
* The C++ code is integrated using Python's native C/C++ extension API

.. seealso::

    For more details on the C/C++ API see

    .. toctree::
       :maxdepth: 1

       c_api

Program file structure
----------------------

The source code is divided into library code (folder ``lib/``) and executable code (folder ``bin/``). The ``bin/`` folder contains the ``pytornado`` command line tool which makes use of the library code.

Library code
~~~~~~~~~~~~

The |name| library is partitioned into files (*modules*) and folders (*packages*). Related *functions* exist within the same module, and related *modules* are grouped within the same package. Short package descriptions:

    * **aero** Core VLM functions (lattice generation, setting up system of equations, etc.).
    * **fileio** All functions related to reading and writing file.
    * **object** Main |name| objects like the aircraft or state.
    * **plot** Functions related to visualisations.
    * **stdfun** Standard top-level procedures, for instance to run a full |name| analysis.

Main |name| objects
-------------------

|name| is written in an object orientated style. There are several objects which turn up in many places in the |name| code base. A brief overview:

    * **Aircraft**
    * **Settings**
    * **State**
    * **VLMLattice**
    * **VLMData**

|name| module descriptions
--------------------------

.. toctree::
   :maxdepth: 1

   modules_main
