# TODO

## Important
* Save plots in '_results'?
* Better autopanneling
* Better system for airfoil modelling (check that camber line rotation axis correct, or better: compute camber line "rotations" as normals of a curved surface?)
* Better "normal rotation" scheme: see Drela with small-angle approximations (would only change RHS!)
* Rename in objects.aircraft
    * WingSegmentSubdivision --> SegmentStrip
    * WingSegmentSubdivisionSubarea --> StripSubdivision
    * --> NOTE: change 'subarea' variables
* Check: `c_results.cpp` --> sign of `results->iw_x[i]` correct?
* Standard value for EPSILON?
* Currently: state file
    - alpha and beta must be given in degrees
    - P, Q, R must be given in radians...!
* Plot spanwise distribution of load (force per meter): get "strip loads"
* Compute stability and control derivatives: see Drela (p.136)
* Reordering of segment vertices (see `cpacs.py`) $\Rightarrow$ better in `objects.models`? (important for boxwing for instance)
* Suspected asymmetric loads (see OptiMale case)
    * Maybe due to panel rotations?
    * Also Fy != 0 although should be
        * Dihedral wings
        * "Interference" with tail?
* Be able to set flight state as desired --> target CL, target Cn etc.
* Hinge axis orientation in global system (always consistent?)
* Subdivision with cosine distribution towards wing tip (how for Boxwing?)
* Can computation of influence matrix be optimized?
   * Eg. exploit matrix symmetry

## Plotting
* Keep track of optional plot parameters somewhere
* Add warning or error if invalid optional key is given
* Visualize far-field velocity field? At cuts parallel to x-axis!?
* Refactor plotting functions
   * (l) Generelise downwash matrix plot
   * Separate 2D/3D plot functions?
   * Reuse plot objects (axes, figures) for efficiency?

## Testing and builds
* Make `tox` work with Anaconda packages (Tigl/Tixi only available through Conda, not on PyPI)
* PyPI: Provide pre-compiled builds
    * Current workaround --> only distribute source code, see also https://www.scivision.dev/easy-upload-to-pypi/
    * Build on TravisCI?
        * https://docs.travis-ci.com/user/deployment/pypi/
        * https://github.com/pypa/python-manylinux-demo
    * Distribute with Conda (less general!)

## JSON files
* (l) Improve structure of the main settings file

## CLI
* The `--clean` option should only affect the project defined in the given settings file (i.e. don't delete everything in *_results* and *_plots* if there are multiple projects)
* Functions `--cpacs2json`
    * Does not work if run from outside the project directory
    * A state file should be created as well if there is a CPACS aeroperformance map
    * Should a new settings file be created as well?

## CPACS support
* AeroPerformanceMaps
    * Save results for remaining parameters in CPACS
        * See: https://www.cpacs.de/documentation/CPACS_3_1_0_RC_Docs/html/e499b429-4ab0-c4f7-9fb4-8cc43b91e894.htm
        * Definition of some coefficients in CPACS is still unclear

### `aero.vlm`
* `pre_panelling`: interpolation of xsi values at segment borders creates curved lines
* Improve auto-panelling algorithm:
    * Generally we want a higher resolution (more chordwise panels) on the control surface (better representation of pressure distribution)
* `pre_panelling`: algorithm assumes correctly ordered segments; is this always given?
* `gen_lattice` (related): Panelling/C-code: rename segments to subarea where necessary to avoid confusion
    * e.g. `lattice.info['num_segment']` should be `lattice.info['num_subarea']`
    * `lattice.info` relevant?
* `gen_lattice()`: `num_r` and `num_p` are the same (clean up)

## Misc
* Aircraft input file: `segment.geometry` useful? Test required
* [`fileio.cpacs`] Currently control surface deflections for the CPACS format are handled using a `/toolspecific` node. Ideally deflections should be read from the CPACS "native" nodes. A few issues with this:
    * Definition of control surface deflection in CPACS is still unclear.
    * How do we deal with `step`s in CPACS? Which deflection shall be used for the analysis?
    * Can asymmetric deflections be defined in CPACS?

## `fileio`
* Verify imported JSON file against schema (!?) Necessary?
* `fileio.model.load()`: Is there a better way?
* `fileio.cpacs`: Incorrect variables for `xsi` (...)
* `fileio.cpacs`: CPACS path for leading egde device data is wrong ==> example file needed

## Issues

### "BOX WING ISSUES"
* In the wing part (at the wing tip) that curves upwards, the normal will "jump" from one side to the other
    * Local effects on normals?
        * Control surface modelling
        * Airfoil (camber line) modelling

## Proposals for other improvements (sometime, prio 3)
* Add a aircraft model generator
    * Simple Python API to generate and serialise aircraft models (--> Maybe later build GUI...?)
* Vertex names should stay more consistent when mirroring (see symmetry 2)
* Is parallelism of segment lines AD and BC enforced?
* Better meshing algorithm?
    * Set "markers" at eta/xsi where to divide... (how do we know what marker belongs to what surface)
* There is a lot of 'copy-and-paste' code in ``c_vlm.cpp`` (make functions instead!)

## Documentation
* Forces in Newton (not Newton per meter) are computed per panel using the Kutta-Joukowski theorem. According to the VLM theory the panel forces act on the center of the quarter-chord line (bound leg of horseshoe vortex)
* The standard horseshoe vortex is h.v. 2 (aligned with free stream), h.v. 0 should be optional (parallel to x)
* CPACS reference length (in CPACS only reference span OR reference chord exists)
    * From CPACS documentation: "In CPACS, only one reference length exists (and is used, e.g. for all three moment coefficients. Coordinates given relative to MAC shall always use this length as MAC."
* Documentation:
    * `rcenter`
    * `gcenter`
* Documentation: Discuss limitations of the software (see e.g. contols in boxwing)

### ON ANGLES:
* Generally, we work with radians in code internally
* Exception
    * Deflections of control surfaces (user input)
    * Angle of attack and side slip angle (user input)
    * Airfoil camber line angle (change this!!!)

## General reminders
* Direction of normal can have influence on the sign of the pressure coefficient
