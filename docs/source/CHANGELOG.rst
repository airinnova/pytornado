Changelog
=========

Changelog for PyTornado. Version numbers try to follow `Semantic
Versioning <https://semver.org/spec/v2.0.0.html>`__.

[0.5.1] -- 2019-10-08
---------------------

Fixed
~~~~~

* Fixed minor bug in CPACS control surface count function (patch) which could raise a Tixi error

Changed
~~~~~~~

[0.5.0] -- 2019-09-23
---------------------

Changed
~~~~~~~

* Changed the mesh deformation API
    * A beam-like deformation field can be attributed to a wing
    * The deformed VLM mesh will be interpolated based on the deformation field

Added
~~~~~

* Optional parameter for *lattice* plot
    * 'deformation': Adds the deformation field points to the lattice plot

[0.4.3] -- 2019-09-06
---------------------

Changed
~~~~~~~

* Updated to `commonlibs` library version 0.2.2 (API changed)

[0.4.2] -- 2019-09-05
---------------------

Changed
~~~~~~~

* Changed the 'plot' settings in the JSON settings file
* Changed the 'save_results' settings in the JSON settings file

[0.4.1] -- 2019-09-03
---------------------

Added
~~~~~

* JSON aircraft files can be serialised from CPACS

Changed
~~~~~~~

* Commonlibs >=2.0.1 is required (new path handling methods were added)
* `io.native.aircraft.load()` saves relative path to airfoil paths (makes PyTornado project directories more portable)

Removed
~~~~~~~

* Horseshoe vortices 'type 0' and 'type 1' removed. Trailing legs of horseshoe vortex should always be aligned with freestream direction (see also Katz and Plotkin, 2001).

[0.4.0] -- 2019-08-28
---------------------

Changed
~~~~~~~

* Simplified section for plot settings in JSON settings file
* Refactored plotting methods
    * More code reuse
    * Common plot operations broken down into separate functions

[0.3.0] -- 2019-08-21
---------------------

Added
~~~~~

* Added support to read AeroPerformanceMaps from CPACS. Results will be written back to the same CPACS file.

Changed
~~~~~~~

* Renamed CLI argument from '--make-wkdir' to '--make-example'
* Simplified structure of the main settings file

Removed
~~~~~~~

* Removed settings 'vlm_lattice' and 'vlm_compute' (use case was unclear)

[0.2.0] -- 2019-08-16
---------------------

Added
~~~~~

* The flight state can be defined using Mach number and altitude. The ICAO standard atmosphere 1993 is used to compute the atmospheric properties at the defined altitude.

Changed
~~~~~~~

* Updated the CPACS import. We now only import CPACS v.>=3.
* Support for control surfaces is still experimental (Tigl does not yet support control surface functions compatible with CPACS v.3)

Removed
~~~~~~~

* Support for CPACS v.2 dropped.

[0.1.0] -- 2019-08-13
---------------------

* First public release

Fixed
~~~~~
