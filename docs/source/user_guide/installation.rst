.. _sec_installation:

Installation
============

|name| is available on the |pypi_long| (PyPI), and it can be installed using the Python package installer pip_. If your have pip_ installed, you can open a terminal and run:

.. code::

    pip install --user pytornado

For a system-wide installation you can omit the ``--user`` flag. However, this may require administrator privileges on your system. To update an existing |name| installation, run:

.. code::

    pip install --user --upgrade pytornado

.. hint::

    **Python requirements:** |name| requires |py_version|. Make sure that you use a correct version of Python. To check your Python version, open a terminal and type ``python --version``.

    .. figure:: _static/terminal.png
       :width: 400 px
       :alt: Terminal
       :align: center

    On some systems the ``python`` command still calls a Python 2 interpreter. In this case try ``python3`` instead.

.. hint::

    **Using pip:** On some systems the ``pip`` command still calls a Python 2 package manager. In this case try ``pip3`` instead.

    .. code::

        pip3 install --user pytornado

.. seealso::

    For more information about pip_, see:

    * https://pip.pypa.io/en/stable/quickstart/
