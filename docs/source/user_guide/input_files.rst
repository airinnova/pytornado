.. _input_files:

Input files
===========

.. note::

    This section discusses the input file when using |name|'s native format (JSON). Note that the inputs can be different if you want to use CPACS_. For the use of CPACS_ please refer to **TODO**

|name| input files are all based on the standardised JSON format. Essentially, JSON files are made up of *keywords* and *data fields*. Using this keyword-data structure arbitrarily complex object definitions can be generated. Notice that there is a very strict syntax. For instance, keywords must be delimited by quantisation marks and brackets must always be closed. If the JSON syntax is invalid |name| will not be able to import the file. Notice also that all keywords and data entries are *case-sensitive* (e.g. ``true`` and ``false`` must be lower-case according to the JSON syntax).

.. image:: _static/images/project_dirs.svg
    :width: 450
    :alt: Project directory
    :align: center

|

.. toctree::
   :maxdepth: 1
   :caption: Detailed description of input files

   input_file_settings.rst
   input_file_aircraft.rst
   input_file_state.rst
   input_file_airfoil.rst
   input_file_deformation.rst

