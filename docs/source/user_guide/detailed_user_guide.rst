.. _detailed_user_guide:

Detailed User Guide
===================

Project directory
-----------------

As seen in the first tutorial (:ref:`getting_started`), |name| has its own *project directory* with several subfolders. |name| can automatically generated the folder structure if necessary. This is what the folder structure typically looks like:

.. figure:: _static/images/project_dirs.svg
   :width: 450
   :alt: Project directory
   :align: center

   Structure of the |name| *project directory*

* ``settings`` The settings folder must contain a *JSON settings file*. This file is the entry point for any VLM analysis. Notice that you referenced this settings file in the first tutorial with the ``--run`` argument (:ref:`getting_started`). The settings file can be named arbitrarily.

* ``aircraft`` This folder contains a file with the aircraft model. |name| reads models stored as JSON or CPACS_ files.

* ``airfoils`` This folder can contain files with airfoil descriptions. Airfoil files can be referenced from the aircraft model (JSON or CPACS_). Airfoil files may be automatically generated if you use CPACS_. Also, if you use |name|'s JSON format, you can define NACA airfoils without adding any files yourself. More information on airfoils can be found here: **TODO**.

* ``state`` TODO

* ``_results`` TODO

* ``_plots`` TODO

* ``log.txt`` This is an automatically generated log file. It contains information about the program execution. Normally, it it only of interest if something went wrong. Then, this log file may contain helpful information.

.. note::

    If you plan to perform analyses for multiple aircraft models, you can separate your analyses by using separate project directories (the top level folder). But it is also possible to keep all analyses in one project folder. Then, you will have multiple settings files in the *settings* folder, multiple aircraft files in your *aircraft* folder etc.

..
    =============================================================================================
    =============================================================================================
    =============================================================================================

**TO BE UPDATED...**


Program execution
-----------------

The program must be executed from the user's project directory, using one of the following commands:

* ``path_to_pyTORNADO/pytornado.py``
* ``python path_to_pyTORNADO/pytornado.py``
* ``python -m path_to_pyTORNADO/pytornado``

Below, available command line arguments are listed:

.. include:: _help_page.txt
    :literal:

To run a VLM calculation based on a given configuration file ``set.NAME_SETTINGS``, the user must provide the extension ``NAME_SETTINGS`` using the argument ``--run``.

* ``--run NAME_SETTINGS``

The user may alternatively wish to call one of a number of utility functions, using the arguments:

    * ``--set_cpacs CPACS STATE`` write PyTORNADO state into CPACS file
    * ``--get_cpacs CPACS`` get PyTORNADO state and aircraft from CPACS file
    * ``--wkdir`` make PyTORNADO project directory template in-place

Optionally, the following mutually exclusive arguments are accepted:

    • ``-q`` or ``--quiet`` for QUIET mode (display error messages only)
    • ``-v`` or ``--verbose`` for VERBOSE mode (display more log messages than usual)
    • ``-d`` or ``--debug`` for DEBUG mode (display all log messages)

Execution procedure
-------------------

When the program is executed, the following steps are performed:

    #. data structures Aircraft, FlightState, Settings, VLMLattice, VLMData, are initialized.
    #. Settings data structure is populated with execution settings from ``set.*`` file.
    #. The aircraft model is loaded into Aircraft from the provided ``aircraft.*`` or ``*.xml`` file.
    #. The aircraft model input data is verified, then the aircraft geometry is generated.
    #. Optionally, the aircraft geometry is displayed.
    #. The flight state data is loaded into FlightState from the provided ``state.*`` file.
    #. The flight state input data is verified, and reference values are copied into FlightState.
    #. Optionally, the discretization settings are automatically generated.
    #. The aircraft lattice is generated, and stored in VLMLattice.
    #. Optionally, the aircraft lattice is displayed.
    #. The aircraft lattice is used to calculate downwash factors.
    #. Optionally, the matrix of downwash factors is displayed.
    #. The aircraft lattice and flight state are used to calculate the right-hand side term.
    #. Vortex strengths are calculated by solving the linear system using LAPACK's dgesv.
    #. Forces, velocities and coefficients are computed.
    #. Optionally, selected results are displayed.

A ``log.txt`` file is generated at each execution to aid in debugging.

.. toctree::
   :maxdepth: 2
   :caption: Input file formats

   input_file_formats.rst
