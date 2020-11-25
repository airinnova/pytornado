Conventions
===========

This page summarises conventions used in the program.

Object hierarchy
----------------

All data related to the aircraft model is contained in the ``Aircraft`` class. Much like in the CPACS_ definition, the aircraft is represented as an assembly of components structured hierarchically:

    * The ``Aircraft`` has lifting surfaces which are instances of class ``Wing``
    * Each ``Wing`` is defined as the assembly of twisted quadrilaterals ``WingSegment``
    * Each ``WingSegment`` is further divided into ``SegmentStrip``
    * Each ``SegmentStrip`` is further divided into ``StripSubdivision``
    * Each ``Wing`` can have control surfaces ``WingControl``

.. figure:: _static/images/basic_hierarchy.svg
   :width: 800 px
   :alt: Basic hierarchy
   :align: center

   Basic object hierarchy. An aircraft object is made up of wings, segments, controls, strips and strip subdivisions.

.. note::

    The user of |name| will only ever have to deal with the defintion of the aircraft, wings and control surfaces. Segment strips and strip subdivisions are internal objects used to facilitate mesh generation for aircraft with control surfaces.
