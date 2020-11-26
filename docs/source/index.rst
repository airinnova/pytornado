Welcome to |name|'s documentation!
==================================

.. figure:: _static/images/logo/logo.svg
   :width: 175 px
   :alt: Logo
   :align: right

Introduction
------------

|name_bold| is an implementation of the |vlm| (VLM). The VLM, based on potential flow theory, is the simplest general method for 3D aerodynamic analyses of aircraft. The method requires only a coarse definition of the aircraft geometry and the flight state. Due to the few input parameters analyses can be set up with little effort. VLM analyses are computationally inexpensive. |name| is an ideal tool for conceptual aircraft design. Short computation times make it possible to easily obtain estimates of aerodynamic loads and to benchmark different concepts.

For simpler analyses |name| provides a simple command line interface. More complex analyses can be setup using the flexible Python API. The aircraft geometry can be defined in a JSON file format or with the CPACS_ format which has been developed by the |dlr_full| (`DLR`_). |name| also provides an API to model *deformed* wings. This makes it possible to perform static *aeroelastic analyses*.

.. figure:: _static/images/main.png
    :scale: 70 %
    :alt: Example
    :align: center

    Aircraft modelled as an assembly of lifting surfaces. The different colors indicate different pressure levels on the wings.

.. toctree::
   :maxdepth: 2
   :caption: User guide

   user_guide/installation
   user_guide/getting_started
   user_guide/model_api_general
   user_guide/model_api
   user_guide/result_api

.. toctree::
    :maxdepth: 2
    :caption: Theory

    theory/index
    theory/coordinate_systems
    theory/global_coeffs

.. toctree::
    :maxdepth: 2
    :caption: Links

    theory/references

.. toctree::
    :maxdepth: 1
    :caption: Contributing

    contribute/index

.. toctree:: :maxdepth: 1
   :caption: Developer documentation

   dev_doc/index
   dev_doc/modules_main

.. toctree::
    :maxdepth: 1
    :caption: Changelog

    CHANGELOG

Licence information
-------------------

|name| is developed at `Airinnova AB`_, Stockholm.

:Authors:
    |author1|,
    |author2|

:Licence:
    |license|
