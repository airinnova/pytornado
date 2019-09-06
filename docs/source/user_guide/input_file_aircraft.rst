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

uid (unique identifier)
-----------------------

The ``uid`` keyword defines the *name* of the aircraft. You may choose any string here. The name will for instance be shown as titles on plots.

refs (reference values for aerodynamic coefficients)
----------------------------------------------------

Aerodynamic coefficients like drag or lift coefficients only have a meaning if the corresponding reference value are known. In |name| you have to explicitly state your reference values. There are five reference values in |name|:

* ``area`` Wing surface area in *meter²*
* ``span`` Wing span in *meter*
* ``chord`` Wing mean aerodynamic chord in *meter*
* ``gcenter`` Centre of gravity in form [:math:`X`, :math:`Y`, :math:`Z`] where :math:`X`, :math:`Y`, :math:`Z` are coordinates (*meter*)
* ``rcenter`` Centre of rotation in form [:math:`X`, :math:`Y`, :math:`Z`] where :math:`X`, :math:`Y`, :math:`Z` are coordinates (*meter*)

How these reference values are used is described in section :ref:`coeffs`.


Symmetry flag
-------------

**TODO** Explain

