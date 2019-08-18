.. _installation:

Installation
============

|name| is written in *Python* and *C++*. At the moment we do not distribute any precompiled versions of |name|. So in order to run |name|, you will have to compile the *C++* code yourself. First, you will need to download the source code, either from `Github`_ or from `PyPI`_:

    * https://github.com/airinnova/pytornado/archive/master.zip
    * https://pypi.org/project/pytornado/#files

.. warning::

    We do provide a |name| package on `PyPI`_. However, the installation with ``pip install pytornado`` will currently result in an incomplete installation due to the uncompiled *C++* code.

After downloading the |name| code, extract the archive and then open a terminal in the root folder of the archive. There should be a file called ``setup.py`` in this folder (if not, the following command will not work). We will use the Python package installer to compile and install |name| and its dependencies. In a command line run:

.. code:: bash

    pip install .

.. todo::
    * setuptools required???

.. seealso::

    How to get started with `pip`_:

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

    |name| has its own *native* file format. To get started it is not necessary to install *Tixi* and *Tigl*.
