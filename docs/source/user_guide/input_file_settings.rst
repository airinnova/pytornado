Settings file
=============

To run any |name| analysis, a settings file is required. All settings are defined in a JSON file which must be located in the **settings** folder of your project directory (see :ref:`project_dir`). An example settings file is shown below.

.. include:: pytornado/settings/template.json
    :code: json

The project file structure corresponding to this settings file will look as follows. Notice where the aircraft and the state file are located.

.. code::

    .
    ├── aircraft
    │   └── template_aircraft.json
    ├── airfoils
    ├── deformation
    ├── log.txt
    ├── _plots
    ├── _results
    ├── settings
    │   └── template.json
    └── state
        └── template.json

Explanation of expected input
-----------------------------

* ``aircraft`` The aircraft key must be followed by the name of the *aircraft file* which is to be loaded. The corresponding aircraft file must be located in the **aircraft** folder of the project directory. The referenced aircraft file may be a JSON file (native format) or a CPACS_ file. |name| will automatically detect the aircraft file type.

* ``state`` The state key must be followed by the name of the *state file* which is to be loaded. The corresponding state file must be located in the **state** folder of the project directory.

.. hint::

    |name| can perform analyses based on the |apm| provided in a CPACS_ file. To load and evaluate a CPACS_ |apm|, the ``state`` field must be followed by the special keyword ``__CPACS``.

    .. code:: json

        "state": "__CPACS",

    Note that the ``aircraft`` must be provided in CPACS_ format. For more information of CPACS_ |apm| analyses see **TODO**

* ``deformation`` **TODO**

* ``vlm_autopanels_c`` **TODO**

* ``vlm_autopanels_s`` **TODO**

* ``save_results`` Analysis results can be written to files for later review and processing. All result files will be saved in the folder **_results**. There are different result files that can be generated. You have to explicitly turn on save operations which is done by writing ``true`` according to the format shown above. The following "sub-keywords" (cf. example above) are available:

    * ``global`` Saves a file with global results (global loads and coefficients).
    * ``panelwise`` Saves a file with "panelwise" results (for instance local panel forces).
    * ``aeroperformance`` Saves a file summarising the results of the |apm| analysis.

.. note::

    * With options ``global`` and ``panelwise`` a new file each is created in every iteration of the |apm| analysis.
    * With option ``aeroperformance`` only a single file is created after the entire |apm| has been evaluated.

* ``plot`` Different kind of plots can be generated during program execution. Plots can either be *shown* in an interactive window during runtime of |name| or *saved* as files. Notice that the program execution is paused when plots are being shown interactively. When files are being saved, they are written to the **_plots** folder. The ``plot`` keyword is followed by a "sub-keywords" which has the following form:

.. code:: json

    "sub-key-name": {
        "opt": ["some_optional_setting", "another_optional_setting"],
        "show": true,
        "save": false
    },

Here, ``opt`` defines some optional setting(s) as a list of strings. The keywords ``show`` and ``save`` are followed by ``true`` or ``false`` to show or save the corresponding plot. Available plots and optional settings:

* ``geometry`` Basic geometry plot showing segments and control surfaces.
    * None
* ``lattice`` Lattice plot showing the VLM mesh.
    * None
* ``results`` Colour plot showing panelwise results.
    * *Panelwise keys* (see **TODO**), example ["cp", "fmag"]
* ``matrix_downwash`` Plot of the VLM downwash matrix.
    * None
