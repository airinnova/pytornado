.. _project_dir:

Project directory
=================

As seen in the first tutorial (:ref:`getting_started`), |name| has its own *project directory* with several subfolders. |name| can automatically generate the folder structure if necessary. This is what the folder structure typically looks like:

.. image:: _static/images/project_dirs.svg
   :width: 450
   :alt: Project directory
   :align: center

|

Folders and files
-----------------

.. image:: _static/images/folder.svg
   :width: 25
   :alt: Folder
   :align: left

**settings** The settings folder must contain a *JSON settings file*. This file is the entry point for any VLM analysis. Notice that you already referenced a settings file in the first tutorial with the ``--run`` argument (:ref:`getting_started`). The settings file can be named arbitrarily.

.. seealso::

    More information on the settings file can be found here: :ref:`input_file_settings`

.. image:: _static/images/folder.svg
   :width: 25
   :alt: Folder
   :align: left

**aircraft** This folder contains a file with the aircraft model. |name| reads models stored as JSON or CPACS_ files.

.. seealso::

    More information on aircraft files can be found here: :ref:`input_file_aircraft`

.. image:: _static/images/folder.svg
   :width: 25
   :alt: Folder
   :align: left

**airfoils** This folder can contain files with airfoil descriptions. Airfoil files can be referenced from the aircraft model (JSON or CPACS_). Airfoil files may be automatically generated if you use CPACS_. Also, if you use |name|'s JSON format, you can define NACA airfoils without adding any files yourself.

.. seealso::

    More information on airfoil files can be found here: :ref:`input_file_airfoils`

.. image:: _static/images/folder.svg
   :width: 25
   :alt: Folder
   :align: left

**state** The *state* directory must contain a file which describes the flight state (or |apm|) which is to be analysed.

.. seealso::

    More information on state files can be found here: :ref:`input_file_state`

.. image:: _static/images/folder.svg
   :width: 25
   :alt: Folder
   :align: left

**_results** This folder and its content are generated during program execution. Numerical results will be stored in files which can be used for further processing. (See :ref:`output_files`)

.. image:: _static/images/folder.svg
   :width: 25
   :alt: Folder
   :align: left

**_plots** Plots can be stored as image files. Plots generated during program execution will be stored in the *_plots* folder. (See :ref:`output_files`)

.. image:: _static/images/file_log.svg
   :width: 50
   :alt: File
   :align: left

**log.txt** This is an automatically generated log file. It contains information about the program execution. Normally, it it only of interest if something went wrong. Then, this log file may contain helpful information.

.. note::

    If you plan to perform analyses for multiple aircraft models, you can separate your analyses by using separate project directories (the top level folder). Alternatively, it is also possible to keep all analyses in one project folder. Then, you will have multiple settings files in the *settings* folder, multiple aircraft files in your *aircraft* folder etc.

.. hint::

    The leading underscores in the folder names **_results** and **_plots** indicate that the folder contents are generated as part of a VLM analysis. The command line arguments ``--clean`` and ``--clean-only`` will delete content in these folders, but other folders remain unaffected (see also :ref:`command_line_interface`).
