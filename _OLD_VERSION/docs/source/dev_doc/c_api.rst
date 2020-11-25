.. _c_api:

Notes on extending Python and Numpy with C
==========================================

|name| contains a module written in C++. All interaction with this module is done via Python's native C/C++ API. The extension module is structured as most such extensions would be. It consists of several files:

    * A ``.h`` header file
    * A ``.cpp`` file containing "wrapper" functions
    * Several ``.cpp`` files containing the actual C routines

An example might help understand how this structure works. Python imports the C++ extension compiled as a dynamic library. In reality, Python only has access to the *wrapper functions* defined in the "wrapper" ``.cpp`` file.

Consider the lattice generation routine. To execute this operation, Python must call the C++ function ``py2c_lattice()`` in the ``c_vlm.cpp`` file. This function is the *wrapper function* for ``vlm_lattice()`` in the ``c_lattice.cpp`` file, which is independent of the Python API. ``py2c_lattice()`` receives the Python data structures containing the pre-allocated data on which ``c_lattice.cpp`` is to operate. These data structures are checked and references to the correct locations in the data structure are extracted using the API, then passed on to the ``c_lattice.cpp`` routine.

.. hint::

    General details on the Python C/C++ extension API can be found here.

        * https://docs.python.org/3/extending/extending.html
        * https://numpy.org/devdocs/reference/c-api/

Header file
-----------

Because the C++ code spans across several files, it is necessary to also include a header file (file extension ``.h``). This file should contain the constants, library imports and function declarations that must be accessible to all functions of the C++ code, across all files. For example, the header file ``c_vlm.h`` contains:

    * ``define`` and ``include`` commands
    * ``typedef`` declarations
    * Constants
    * Function declarations

One should note that the expressions

.. code:: c

    #include <Python.h>

and

.. code:: c

    #define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
    #include <numpy/arrayobject.h>

are specific to the Python and Numpy APIs, respectively, and must be included in order to access the objects and functions that are used to pass data back and forth between the programming languages.

Wrapper
-------

The wrapper is where those functions are defined, that will be called directly from Python. The intended role for these wrapper functions is to check the incoming Python data structures, and to create references to the relevant data using the Python API.

Ideally, this is done in such a way that the Python API is invoked only in the wrapper functions. In other words, the referenced data should be formatted so that it may be operated on directly by routines written purely in C. Since the Vortex-Lattice Method involves large arrays of data, this is especially important: copying or conversion of data would incur non-negligible computational costs.

The *NumPy* array format allows this, as it consists of a contiguous memory block (containing the actual data) and some metadata (size, shape, type, etc.). This is otherwise not true for most Python types, as these are really objects -- even numbers! Therefore, the wrapper functions must rely more heavily on the API to convert these to C types.

In |name|, the wrapper file ``c_vlm.cpp`` contains the code for interpreting Python input data in separate functions, one for each data structure. This way, if the data structure has been modified, the wrapper must be adapted only in one location. These functions are named ``get_*`` and ``set_*`` because they also create references to relevant data and give these references to the C structs used in the remaining C routines.

Once the referenced data has been checked and has been made readable as a C type, the wrapper function should call the actual C routine that operates on said data.

When finished, the wrapper function should return ``Py_None`` (Python's ``None`` - also an object!). Since we are creating this new Python object to return it to the caller, we must increase the reference count to this object by adding ``Py_INCREF(Py_None)`` before the return statement. I would recommend that the reader also reads the documentation on reference counting in extensions:

    * https://docs.python.org/3/extending/extending.html#reference-counts
