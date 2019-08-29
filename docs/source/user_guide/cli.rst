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

**Logging**

Logging information can be printed to the terminal screen and written to a log file. Logging information can be printed with different levels. These arguments are ``-debug`` or ``--d`` (most amount of information), ``-verbose`` or ``--v`` (normal amount) and ``-quiet`` or ``--q`` (only errors). By default, |name| is quiet.

.. note::

    Error messages will always be printed (even in quiet mode).

**Cleaning up previous result files**

Sometimes, it can be useful to remove result files from previous analyses. Instead of removing files by hand, |name_cli| provides arguments to clean up from previous analyses. If you pass the flag ``--clean`` or ``-c`` result files from all previous analyses will be removed before a new VLM analysis is started. Note that only files in the directories **_results** and **_plots** are affected.

If you do not want to start a new analysis you can use ``--clean-only`` which will remove old result files but not invoke a new VLM analysis.

.. hint::

    You can combine several arguments like this:

    .. code::

        pytornado -cvr settings/template.json

    |name| will clean up the **_results** and **_plots** directories (if there are files from previous analyses) and then a VLM will be started in verbose mode.

**Creating a template project**

If you start with a new project, |name| allows you to easily generate a clean project directory and a minimalistic example is generated (see also :ref:`getting_started`).

.. code::

    pytornado --make-example

**Converting CPACS to JSON**

TODO

.. code::

    pytornado --cpacs2json path/to/CPACS_file.xml
