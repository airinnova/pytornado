.. _input_file_aircraft:

Aircraft file
=============

An aircraft file defines the (undeformed) geometry of an aircraft. Aircraft models are defined using a hierarchical system. An **aircraft** is made up of one or more **wings**. Each wing may be divided into **segments** (a quadrilateral), and each wing may also have **control surfaces**.

.. figure:: _static/images/aircraft_hierarchy.svg
    :width: 550
    :alt: Aircraft model
    :align: center

    An *aircraft* is broken down into *wings* and a wing is broken down into *segments*. Each wing can have any number of *control surfaces*. (Note that *segment strips* and *strip subdivisions* are part of |name|'s internal API. However, they are not relevant for the model input discussed here.)

The aircraft definition file closely resembles the this hierarchical structure. A fairly simple example is shown below.

.. include:: pytornado/aircraft/template_aircraft.json
    :code: json

Aircraft: uid (unique identifier)
---------------------------------

The ``uid`` keyword defines the *name* of the aircraft. You may choose any string here. The name will for instance be shown as titles on plots.

Aircraft: refs (reference values for aerodynamic coefficients)
--------------------------------------------------------------

Aerodynamic coefficients like drag or lift coefficients only have a meaning if the corresponding reference value are known. In |name|, reference values have to explicitly defined. There are five reference values in |name|:

* ``area`` Wing surface area in [:math:`m^2`]
* ``span`` Wing span in [:math:`m`]
* ``chord`` Wing mean aerodynamic chord in [:math:`m`]
* ``gcenter`` Centre of gravity in form [:math:`X`, :math:`Y`, :math:`Z`] where :math:`X`, :math:`Y`, :math:`Z` are coordinates [:math:`m`]
* ``rcenter`` Centre of rotation in form [:math:`X`, :math:`Y`, :math:`Z`] where :math:`X`, :math:`Y`, :math:`Z` are coordinates [:math:`m`]

How these reference values are used is described in section :ref:`coeffs`.

Aircraft: wings (wing object)
-----------------------------

Wing: uid (unique identifier)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Wing: symmetry (symmetry flag)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Wing: segments (symmetry objects)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Segments: uid (unique identifier)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Segments: vertices
^^^^^^^^^^^^^^^^^^

Segments: geometry
^^^^^^^^^^^^^^^^^^

Segments: airfoils
^^^^^^^^^^^^^^^^^^

Segments: panels
^^^^^^^^^^^^^^^^

Wing: controls
~~~~~~~~~~~~~~

Control: uid (unique identifier)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Control: device_type
^^^^^^^^^^^^^^^^^^^^

Control: deflection
^^^^^^^^^^^^^^^^^^^

Control: deflection_mirror
^^^^^^^^^^^^^^^^^^^^^^^^^^

Control: segment_uid
^^^^^^^^^^^^^^^^^^^^

Control: rel_vertices
^^^^^^^^^^^^^^^^^^^^^

Control: rel_hinge_vertices
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Control: panels
^^^^^^^^^^^^^^^

**TODO** Explain

