.. _command_line_interface:

The command line interface
==========================

|name| provides a command line tool which can be used to start VLM analyses. The executable is called |name_cli|. If you simply run |name_cli| in a terminal without any arguments, a simple help page will be printed.

.. include:: _help_page.txt
    :literal:

**Pointing to a settings file**

Perhaps the most important argument is ``--run`` (or short ``-r``). This argument must be followed by a file path to the |name| settings file. Notice that you used this argument in the first tutorial (:ref:`getting_started`) where the settings file was located at ``settings/template.json``.

.. code::

    pytornado --run settings/template.json

.. hint::

    You can provide the settings file path as any relative or absolute file path. |name| will automatically detect the project directory. Of course, the other project subdirectories including the *aircraft* and *state* files must exist in a structure described in :ref:`project_dir`.

**Logging**

Logging information can be printed to the terminal screen and written to a log file. Arguments determine the amount of printed information. The argument ``-debug`` or ``--d`` will print the most amount of information, ``-verbose`` or ``--v`` will ignore less relevant information and ``-quiet`` or ``--q`` will only print errors. By default, |name| is quiet.

.. note::

    *Error messages* will always be printed (even in quiet mode).

**Cleaning up previous result files**

Sometimes, it can be useful to remove result files from previous analyses. Instead of removing files by hand, |name_cli| provides arguments to clean up from previous analyses. If you pass the flag ``--clean`` or ``-c`` result files from all previous analyses will be removed before a new VLM analysis is started. Note that only files in the directories **_results** and **_plots** are affected.

If you do not want to start a new analysis you can use ``--clean-only`` which will remove old result files but not invoke a new VLM analysis.

.. hint::

    Note that you can combine several arguments like this:

    .. code::

        pytornado -cvr settings/template.json

    |name| will clean up the **_results** and **_plots** directories (if there are files from previous analyses) and then a VLM will be started in verbose mode.

**Creating a template project**

If you start with a new project, |name| allows you to easily generate a clean project directory including minimalistic working example (see also :ref:`getting_started`).

.. code::

    pytornado --make-example

**Converting CPACS to JSON**

|name|'s native JSON format has a simpler and flatter structure than CPACS_. Sometimes, it may be more convenient to edit the aircraft definition using the JSON format rather than CPACS_. CPACS_ files can easily be converted to JSON. Change into a project directory (see :ref:`project_dir`) with a CPACS_ file in the *aircraft* subdirectory. Now you may run:

.. code::

    pytornado --cpacs2json aircraft/CPACS_file.xml

The CPACS_ file ``aircraft/CPACS_file.xml`` will be loaded and a new file ``aircraft/CPACS_file.json`` will be created. Notice that the file extension of the new file is ``.json``.

.. warning::

    An existing file ``aircraft/CPACS_file.json`` will be overwritten.

To use the new JSON file instead of CPACS_ you will have to edit your main settings file (:ref:`input_files`).

**General notes**

.. note::

    Besides the command line interface |name| also provides a Python API through which analyses can be setup.

    * See :ref:`python_api`
