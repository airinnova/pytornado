.. _installation:

Installation
============

|name| is written in *Python* and *C++*. At the moment we do not distribute any precompiled versions. In order to run |name|, you will have to compile the *C++* code yourself.

Prerequisites
-------------

Linux
~~~~~

Make sure that the Python package manager pip_ (for Python 3.x) is installed. In addition, Numpy is needed for the installation as it provides some C++ header files. You can install pip_ and Numpy from a terminal by running the following commands (tested with *Ubuntu 18.04*):

.. code:: bash

    sudo apt install python3-pip
    pip3 install --user numpy

MacOS
~~~~~

*to be upadated*

Windows
~~~~~~~

To compile the *C++* code on Windows *Microsoft Visual C++* is needed. The software can be downloaded here:

* https://visualstudio.microsoft.com/downloads/

Also make sure to setup your ``PATH`` and ``PYTHONPATH`` environment variables correctly.

* https://docs.python.org/3/using/windows.html#excursus-setting-environment-variables
* https://superuser.com/questions/143119/how-do-i-add-python-to-the-windows-path

User installation
-----------------

First, you will need to download the source code from `Github`_:

    * https://github.com/airinnova/pytornado/archive/master.zip

After downloading the |name| source code, extract the archive and then open a terminal in the root folder of the archive. There should be a file called ``setup.py`` in this folder (if not, the following command will not work). We will use the Python package installer (pip_) to compile and install |name| and its dependencies. In a command line run:

.. code:: bash

    pip install --user .

.. note::

    * It is recommended to run the installation with the ``--user`` flag. If you know what you are doing, you can modify this setting.
    * On Linux/Ubuntu the executable may be called ``pip3`` instead of ``pip``.

.. seealso::

    How to get started with pip_:

    * https://pip.pypa.io/en/stable/quickstart/

That's it! If the command ran successfully, |name| is now installed on your system. If you are having troubles with the installation, please send us a message:

    * https://github.com/airinnova/pytornado/issues

Basic requirements
------------------

*Python 3.6* or higher is required. Additional Python libraries used by |name| will be installed automatically when you follow the instructions above.

Optional requirements
---------------------

|name| fully supports the `CPACS`_ format developed by the DLR_. If you intend to use `CPACS`_  you will have to install two additional libraries:

    * Tixi (https://github.com/DLR-SC/tixi)
    * Tigl (https://github.com/DLR-SC/tigl)

Please refer to the Tixi and Tigl documentation for installation guides.

.. hint::

    |name| has its own *native* JSON file format. To get started it is not necessary to install *Tixi* and *Tigl*.

.. warning::

    We do provide a |name| package on `PyPI`_. However, the installation with ``pip install pytornado`` will currently result in an incomplete installation due to the uncompiled *C++* code.
