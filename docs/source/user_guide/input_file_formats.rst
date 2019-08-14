Files
=====

**TO BE UPDATED...**

The program performs the tasks specified in the set file without user intervention, relying completely on the input files and arguments provided upon execution.

For a typical VLM calculation, the program must be provided the following files:

    * ``aircraft.name`` or ``name.xml``	aircraft definition for aircraft "name", in aircraft
    * ``blade.name`` airfoil coordinates for airfoil "name”, in airfoils
    * ``state.name`` flight state definition for flight state "name", in state
    * ``set.name`` execution settings for case "name", in settings

The name of the aircraft and state files should be provided in the set file. The airfoil coordinate files should be referenced in the definition of the aircraft wing segments.

The format of the CPACS and |name| input files is commented in detail in ....

|name|'s native aircraft definiton format
-----------------------------------------

For simple wings and for testing/debugging purposes, it may be unnecessary to employ the rather comprehensive CPACS format. PyTORNADO allows the user to manually define the aircraft (its wings, segments and their properties) using a simpler, human-readable text format.

The format of the text file follows the hierarchical composition of the Aircraft data structure naturally. Shown below is a template defining an aircraft with a single wing, composed of a single segment and a control device. Naturally, multiple segments can be used to define a wing, which can have multiple control devices, and the aircraft may have more than one wing.

|name|'s native state definiton format
---------------------------------------

Currently, the input data for the flight state must be entered in a |name| text file ``state.*``, in the state directory of the user's In the future, this input data will be found in a ``toolspecifc/pyTORNADO`` node of the CPACS file.

The syntax of the ``state.*`` files is similar to that of the ``aircraft.*`` files. No hierarchical structure is required, only a small number of parameters must be specified.

Description
~~~~~~~~~~~

* ``aero.airspeed`` is the magnitude of the far-field flow velocity. aero.airspeed must be a positive real number.
* ``aero.density`` is the air density. aero.density must be a positive real number.
* ``aero.alpha`` is the angle of attack. aero.alpha must be a positive real number between -90.0 and +90.0 (degrees).
* ``aero.beta`` is the angle of attack. aero.beta must be a positive real number between -90.0 and +90.0 (degrees).
* ``aero.rate_P`` is the rate of rotation about the x-axis. aero.rate_P must be a positive real number.
* ``aero.rate_Q`` is the rate of rotation about the y-axis. aero.rate_Q must be a positive real number.
* ``aero.rate_R`` is the rate of rotation about the z-axis. aero.rate_R must be a positive real number.

|name|'s native settings definiton format
-----------------------------------------

The ``set.*`` settings file in the settings folder acts as a configuration file for |name|. It contains information on the location of the input data, on the analysis tasks to be performed and plots to be generated.

The syntax of the ``set.*`` files is similar to that of the ``aircraft.*`` files. No hierarchical structure is required, only a small number of parameters must be specified.

Description
~~~~~~~~~~~

    * ``inputs.aircraft`` is the extension of the ``aircraft.*`` file to be used as input for the aircraft model. If provided, inputs.aircraft must be a string of alphanumeric characters, underscores and dashes. If not, it should be omitted or set to ``NONE.`` The corresponding ``aircraft.*`` file must be located in the aircraft folder of the project directory.
    * ``inputs.cpacs`` is the extension of the ``*.xml`` CPACS file to be used as input for the aircraft model. If provided, ``inputs.cpacs`` must be a string of alphanumeric characters, underscores and dashes. If not, it should be omitted or set to ``NONE.`` The corresponding ``*.xml`` file must be located in the aircraft folder of the project directory.
    * ``inputs.state`` is the extension of the ``state.*`` file to be used as input for the flight state. ``inputs.state`` must be a string of alphanumeric characters, underscores and dashes. The corresponding ``state.*`` file must be located in the state folder of the project directory.
    * ``outputs.vlm_autopanels`` is a parameter used in the automatic generation of the lattice. It corresponds to the number of panels to be applied along the chord of the main wing (the wing with the largest average chord) of the aircraft. The remaining parameters are calculated as to minimize aspect ratio while keeping consistent panel size. If this feature is desired, ``outputs.vlm_autopanels`` should be a positive integer, otherwise, it should be omitted or set to 0.
    * ``outputs.vlm_lattice`` indicates whether |name| should generate a lattice for the aircraft model. ``outputs.vlm_lattice`` must be ``TRUE`` or ``FALSE.`` If ``FALSE,`` no VLM calculation can be performed.
    * ``outputs.vlm_results`` indicates whether |name| should calculate results of the VLM analysis. ``outputs.vlm_results`` must be ``TRUE`` or ``FALSE.``
    * ``plot.geometry_aircraft`` indicates whether |name| should generate 3D and 2D views of the aircraft geometry. ``plot.geometry_aircraft`` must be ``TRUE`` or ``FALSE.``
    * ``plot.geometry_wing`` indicates whether |name| should generate a 3D view of selected wings. ``plot.geometry_wing`` must be a list of the selected wing names.
    * ``plot.geometry_segment`` indicates whether |name| should generate a 3D view of selected wing segments. ``plot.geometry_segment`` must be a list of the selected segment names.
    * ``plot.geometry_property`` indicates whether |name| should generate plots of the distribution of selected segment geometry properties along the span of the wings listed in ``plot.geometry_wing.`` ``plot.geometry_property`` must be a list of the selected properties (e.g. ``inner_chord``; ``span``; ...).
    * ``plot.lattice_aircraft`` indicates whether |name| should generate 3D and 2D views of the aircraft lattice. ``plot.lattice_aircraft`` must be ``TRUE`` or ``FALSE.``
    * ``plot.lattice_wing`` indicates whether |name| should generate a 3D view of the lattice for selected wings. ``plot.lattice_wing`` must be a list of the selected wing names.
    * ``plot.lattice_segment`` indicates whether |name| should generate a 3D view of the lattice for selected wing segments. ``plot.lattice_segment`` must be a list of the selected segment names.
    * ``plot.results_downwash`` indicates whether |name| should generate a colormap visualisation of the downwash coefficient matrix. ``plot.results_downash`` must be ``TRUE`` or ``FALSE.``
    * ``plot.results_panelwise`` indicates whether |name| should generate a 3D view of aircraft lattice with a colormap overlay of the distribution of selected results. ``plot.results_panelwise`` must be a list of the selected variables (e.g. ``vx``; ``fmag``; ``gamma``; ``cp,`` ...).
