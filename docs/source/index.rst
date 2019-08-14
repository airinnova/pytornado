Welcome to |name|'s documentation!
==================================

.. image:: _static/images/logo/logo006.svg
   :width: 150 px
   :alt: Logo
   :align: right

Introduction
------------

|name_bold| is a Python/C++ implementation of the |vlm|
(VLM). A main objective is the automation of the geometry definition, the
meshing and the CFD analysis itself. This allows |name| to be integrated into
highly automated frameworks. The aircraft geometry can be defined in a |name|
JSON file format or using CPACS_. |name| also has the capability to perform
analyses of deformed wings and thus can be used for static aeroelastic analyses.

.. image:: _static/images/main.png
   :scale: 50 %
   :alt: Example
   :align: center

.. toctree::
   :maxdepth: 2
   :caption: User guide

   user_guide/what_is
   user_guide/requirements
   user_guide/getting_started
   user_guide/detailed_user_guide
   user_guide/caveats

.. toctree::
   :maxdepth: 1
   :caption: Changelog

   CHANGELOG

.. toctree::
   :maxdepth: 1
   :caption: Developer documentation

   dev_doc/program_structure
   dev_doc/conventions
   dev_doc/theory
   dev_doc/modules_main

Licence information
-------------------

|name| was developed at `Airinnova AB`_, Stockholm.

:Authors:
    |author1|,
    |author2|

:Licence:
    |license|
