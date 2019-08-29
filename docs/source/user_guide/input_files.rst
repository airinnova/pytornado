Input files
===========

.. note::

    This section discusses the input file when using |name|'s native format (JSON). Note that the inputs can be different if you want to use CPACS_. For the use of CPACS_ please refer to **TODO**

|name| input files are all based on the standardised JSON format. Essentially, JSON files are made up of *keywords* and *data fields*. Using this keyword-data structure arbitrarily complex object definitions can be generated. Notice that there is a very strict syntax. For instance, keywords must be delimited by quantisation marks and brackets must always be closed. If the JSON syntax is invalid |name| will not be able to import the file.

.. image:: _static/images/project_dirs.svg
    :width: 450
    :alt: Project directory
    :align: center

|

Settings file
-------------

To run any |name| analysis, a settings file is required. All settings are defined in a JSON file which must be located in the **settings** folder of your project directory (:ref:`project_dir`). An example settings file is shown below.

.. include:: pytornado/settings/template.json
    :code: json

**TODO** Explain

Aircraft file
-------------

An aircraft file defines the (undeformed) geometry of an aircraft. Aircraft models are defined using a hierarchical system. An **aircraft** is made up of one or more **wings**. Each wing may be divided into **segments** (a quadrilateral), and each wing may also have **control surfaces**.

.. figure:: _static/images/aircraft_hierarchy.svg
    :width: 550
    :alt: Aircraft model
    :align: center

    An *aircraft* is broken down into *wings* and a wing is broken down into *segments*. Each wing can have any number of *control surfaces*. (Note that *segment strips* and *strip subdivisions* are part of |name|'s internal API. However, they are not relevant for the model input discussed here.)

.. include:: pytornado/aircraft/template_aircraft.json
    :code: json

**TODO** Explain

State file
----------

.. include:: pytornado/state/template.json
    :code: json

**TODO** Explain

Airfoil files
-------------

**TODO**

Deformation file
----------------

**TODO**
