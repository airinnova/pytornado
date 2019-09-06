.. _input_files:

Input files
===========

.. note::

    This section first discusses the input files when using |name|'s native format (JSON). Note that the inputs can be different if you want to use CPACS_. For the use of CPACS_ please refer to :ref:`input_file_cpacs`.

|name| input files are all based on the standardised JSON format. Essentially, JSON files are made up of *keywords* and *data fields*. Using this keyword-data structure arbitrarily complex object definitions can be generated. Notice that there is a very strict syntax. For instance, keywords must be delimited by quantisation marks and brackets must always be closed. If the JSON syntax is invalid |name| will not be able to import the file. Notice also that all keywords and data entries are *case-sensitive* (e.g. ``true`` and ``false`` must be lower-case according to the JSON syntax).

.. image:: _static/images/project_dirs.svg
    :width: 450
    :alt: Project directory
    :align: center

|

.. toctree::
   :maxdepth: 1
   :caption: Detailed description of input files

   input_file_settings
   input_file_aircraft
   input_file_state
   input_file_airfoil
   input_file_deformation

.. toctree::
   :maxdepth: 1
   :caption: Using CPACS

   input_file_cpacs
