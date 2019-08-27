# TODO

* Update 'os.path.join()' calls

* Improve structure of the main settings file
    * Better 'plots' solution!

* Refactor CPACS functions --> make control surfaces work

* Bug with Cm coefficient (may there is some unassigned value in the C++ code, check reference values...)

* Fix PyPI (binaries?)

## CPACS support

* AeroPerformanceMaps
    * Save results for remaining parameters in CPACS
        * See: https://www.cpacs.de/documentation/CPACS_3_1_0_RC_Docs/html/e499b429-4ab0-c4f7-9fb4-8cc43b91e894.htm
        * Definition of some coefficients in CPACS is still unclear

## Important
* Better system for airfoil modelling (check that camber line rotation axis correct, or better: compute camber line "roatations" as normals of a curved surface?)
* Check: `c_results.cpp` --> sign of `results->iw_x[i]` correct?
* Sweep analysis --> compute and store results for a range of input parameters (e.g. $\alpha$, $\beta$, $u$, etc.). Re-compute the "RHS".
    * Input for sweep computations should be set in `state/` file (e.g. as `aero.alpha = 5, 10, 15`)
    * Where should this be defined by the user? (CPACS, native format)
* JSON: make airfoil paths *relative*
* Standard value for EPSILON?
* Hide underscore settings from user when creating a template directory
* Currently: state file
    - alpha and beta must be given in degrees
    - P, Q, R must be given in radians...!
* Plot spanwise distribution of load (force per meter): get "strip loads"
* Documentation:
    * `rcenter`
    * `gcenter`
* Compute stability and control derivatives: see Drela (p.136)
* Better "normal rotation" scheme: see Drela with small-angle approximations (would only change RHS!)
* Reordering of segment vertices (see `cpacs.py`) $\Rightarrow$ better in `objects.models`? (important for boxwing for instance)
* Suspected asymmetric loads (see OptiMale case)
    * Maybe due to panel rotations?
    * Also Fy != 0 although should be
        * Dihedral wings
        * "Interference" with tail?
* Be able to set flight state as desired --> target CL, target Cn etc.
* Use `pathlib` for files
* Rename:
    * "subdivision": "strip"??
    * "subarea": ??

### `aero.vlm`
* `pre_panelling`: interpolation of xsi values at segment borders creates curved lines
* Improve auto-panelling algorithm:
    * Generally we want a higher resolution (more chordwise panels) on the control surface (better representation of pressure distribution)
* `pre_panelling`: algorithm assumes correctly ordered segments; is this always given?
* `gen_lattice` (related): Panelling/C-code: rename segments to subarea where necessary to avoid confusion
    * e.g. `lattice.info['num_segment']` should be `lattice.info['num_subarea']`
    * `lattice.info` relevant?
* `gen_lattice()`: `num_r` and `num_p` are the same (clean up)

## CPACS
* Write back to CPACS format

## Misc
* Documentation: Discuss limitations of the software (see e.g. contols in boxwing)
* `plot.results`: 3-side view: no colours (!)
* `fileio.results`: saving loads with undeformed deformed mesh does not work at same time
* Aircraft input file: `segment.geometry` useful?
* [`fileio.cpacs`] Currently control surface deflections for the CPACS format are handled using a `/toolspecific` node. Ideally deflections should be read from the CPACS "native" nodes. A few issues with this:
    * Definition of control surface deflection in CPACS is still unclear.
    * How do we deal with `step`s in CPACS? Which deflection shall be used for the analysis?
    * Can asymmetric deflections be defined in CPACS?

## `fileio`
* Verify imported JSON file against schema (!?) Necessary?
* `fileio.model.load()`: Is there a better way?
* `fileio.results.save_panelwise()` --> make faster version
* `fileio.cpacs`: Incorrect variables for `xsi` (...)
* `fileio.cpacs`: CPACS path for leading egde device data is wrong ==> example file needed
* `fileio.cpacs`: coefficients should be written back to CPACS (/toolspecific/PyTornado/aeroPerformanceMap)
* `fileio.cpacs`: When importing from CPACS or XML-AeroMap use altitude node for density calculation

## Airfoils
* Implement more accurate camber line method ("Jesper method")
* Thorough testing of NACA airfoil generator
* Implement generator for for NACA 6-digit series (etc.) and user input

## Reference values
* Reference values ($S$, $MAC$, $b$) for coefficient should not be computed by Tornado, but be defined by the user!? (talk to Jesper)

## General
* Hinge axis orientation in global system (always consistent?)
* Subdivision with cosine distribution towards wing tip (how for Boxwing?)

## "BOX WING ISSUES"
* In the wing part (at the wing tip) that curves upwards, the normal will "jump" from one side to the other
    * Local effects on normals?
        * Control surface modelling
        * Airfoil (camber line) modelling

## Proposals for other improvements (sometime, prio 3)
* Vertex names should stay more consistent when mirroring (see symmetry 2)
* Some `plot` modules use the exact same code ==> outsource common code and reuse!
    * Perhaps store commonly used plot object in a dict?
* Bash autocompletion for `--run` argument (or allow full path to settings file)
* CPACS 3.0 compatibility
* `objects.model`: `get_point()` method in class `Wing` is obsolete (understand \& remove)
* Is parallelism of segment lines AD and BC enforced?
* Better meshing algorithm?
    * Set "markers" at eta/xsi where to divide... (how do we know what marker belongs to what surface)

## Documentation
* Forces in Newton (not Newton per meter) are computed per panel using the Kutta-Joukowski theorem. According to the VLM theory the panel forces act on the center of the quarter-chord line (bound leg of horseshoe vortex)
* The standard horseshoe vortex is h.v. 2 (aligned with free stream), h.v. 0 should be optional (parallel to x)
* CPACS reference length (in CPACS only reference span OR reference chord exists)
    * From CPACS documentation: "In CPACS, only one reference length exists (and is used, e.g. for all three moment coefficients. Coordinates given relative to MAC shall always use this length as MAC."

### ON ANGLES:
* Generally, we work with radians in code internally
* Exception
    * Deflections of control surfaces (user input)
    * Angle of attack and side slip angle (user input)
    * Airfoil camber line angle (change this!!!)

## Other requirements
* "Python3.6-devel" is required for "Python.h" header file (i.e. to compile the C/C++ code)
* `tkinter` may have to be installed separately for matplotlib to work (not included in matplotlib PyPI package?)

### Error with matplotlib version 3.1.1 (2019-08-14)

* Matplotlib version 3.1.1 throws NotImplementedError! Force version 3.0.2 for now

```
Traceback (most recent call last):
  File "main.py", line 57, in <module>
    pyt.standard_run(args)
  File ".../pytornado/stdfun.py", line 193, in standard_run
    pl_geometry.view_aircraft(aircraft, plt_settings, plot='norm')
  File ".../pytornado/plot/geometry.py", line 77, in view_aircraft
    axes_xyz.set_aspect('equal')
  File ".../matplotlib/axes/_base.py", line 1281, in set_aspect
    'It is not currently possible to manually set the aspect '
NotImplementedError: It is not currently possible to manually set the aspect on 3D axes
```

## General reminders
* Direction of normal can have influence on the sign of the pressure coefficient

## PyPI
* Provide pre-compiled builds (current workaround --> only distribute source code, see also https://www.scivision.dev/easy-upload-to-pypi/)
