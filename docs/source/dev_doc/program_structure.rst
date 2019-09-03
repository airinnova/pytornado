Program structure
=================

**TO BE UPDATED...**

.. figure:: _static/images/meshing_with_controls.svg
   :width: 600 px
   :alt: Meshing algorithm
   :align: center

   Meshing algorithm

Aerofoil and control surface modelling by modification of the flow tangency boundary condition using normal rotations

.. image:: _static/images/normal_rotations_controls.svg
   :width: 600 px
   :alt: Control surface modelling
   :align: center

.. image:: _static/images/normal_rotations_airfoils.svg
   :width: 300 px
   :alt: Airfoil modelling
   :align: center

.. image:: _static/images/normal_rotations_airfoils.svg
   :width: 300 px
   :alt: Airfoil modelling
   :align: center

.. image:: _static/images/mesh_deformations.svg
   :width: 400 px
   :alt: Mesh deformation
   :align: center

Data structures
---------------

Aircraft
~~~~~~~~

The Aircraft data structure contains the entire aircraft model. An aircraft model is identified by its attribute name, accessed by using aircraft.name.

A number of reference values must be provided as properties of the aircraft model. These are stored in a dictionary, the Aircraft.refs attribute:

    * ``area`` reference surface area
    * ``span`` reference (semi-)span
    * ``chord`` reference chord
    * ``gcenter`` center of gravity (x, y, z-coordinates)
    * ``rcenter`` reference rotation point (x, y, z-coordinates)

Wing
~~~~

Each Wing object contains data, properties and components of a given lifting surface. Each wing is identified by its index in Aircraft.wing.

Symmetry
________

The Wing.symmetry attribute defines symmetry for the entire lifting surface. Accepted values are:

    * 0	no symmetry
    * 1	symmetry across y, z-plane
    * 2	symmetry across x, z-plane
    * 3	symmetry across x, y-plane

Wing controls
~~~~~~~~~~~~~

The WingControl sub-components of Wing are stored in its Wing.control attribute. Each WingControl must have a unique identifier, which is used to access it in Wing.control.

Wing segment
~~~~~~~~~~~~

Each WingSegment object contains data and properties of a quadrilateral segment of lifting surface. Each segment is identified by its index in Wing.segment.

Vertices
________

The x, y, z-coordinates of each of the four corner points A, B, C, D of the quadrilateral segment are stored in the dictionary WingSegment.vertices.

The vertices are re-ordered so that the orientation of the segment’s normal vector is consistent.

Geometric properties
^^^^^^^^^^^^^^^^^^^^

The geometric properties of each segment are stored in the dictionary WingSegment.geometry. These are listed and described below:

    * ``inner_chord`` chord of segment edge AD
    * ``inner_alpha`` incidence angle of segment edge AD
    * ``inner_beta`` yaw angle of segment edge AD
    * ``inner_axis`` position of twist axis on segment edge AD as fraction of inner_chord
    * ``outer_chord`` chord of segment edge BC
    * ``outer_alpha`` incidence angle of segment edge BC
    * ``outer_beta`` yaw angle of segment edge BC
    * ``outer_axis`` position of twist axis on segment edge BC as fraction of outer_chord
    * ``span`` span of segment, taken along twist axis
    * ``sweep`` sweep of segment, measured at leading edge
    * ``dihedral`` dihedral of segment, measured at twist axis1.3.76

The geometry of each lifting surface segment is generated from a combination of provided corner points and geometric parameters. The accepted combinations are:

    * All of the vertices A, B, C and D and no geometric properties.
    * Vertices A and D and all geometric properties, except those beginning with ``inner_*``
    * Vertices B and C and all geometric properties, except those beginning with ``outer_*``
    * One of the vertices A, B, C or D and all geometric properties.

Wing control
~~~~~~~~~~~~

Each WingControl object contains data and properties of a control surface (flap or slat). Each control surface is identified by its index in Wing.control.
