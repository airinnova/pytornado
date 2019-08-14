Notes on extending Python and Numpy with C
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. warning::

    This page is deprecated and must be updated. This article was written for Python version 2, but |name| is now using Python 3 is now using Python 3.

Overview
^^^^^^^^

The Python extension in C for calculations using the Vortex-Lattice Method is structured as most such extensions would be. It consists of several files, which are described more in detail in this document:

    * a ``.h`` header file
    * a ``.cpp`` file containing "wrapper" functions
    * several ``.cpp`` files containing the actual C routines

An example might help understand how this structure works. Python imports the C extension compiled as a dynamic library. In reality, Python only has access to the wrapper functions defined in the "wrapper" ``.cpp`` file.

Consider the lattice generation routine. To execute this operation, Python must call the C function ``py2c_lattice`` in the ``c_vlm.cpp`` file. This function is the wrapper function for ``vlm_lattice`` in the ``c_lattice.cpp`` file, which is independent of the Python API. ``py2c_lattice`` receives the Python data structures containing the pre-allocated data on which ``c_lattice.cpp`` is to operate. These data structures are checked and references to the correct locations in the data structure are extracted using the API, then passed on to the ``c_lattice.cpp`` routine.

Header file
^^^^^^^^^^^

Because the C code spans across several files, it is necessary to include also a ``.h`` header file. This file should contain the constants, library imports, constants and function declarations that must be accessible to all functions of the C code, across all files.

For example, the header file ``c_vlm.h`` contains:

* ``define`` and ``include`` commands
* ``typedef`` declarations
* constants
* function declarations

One should note that the expressions

    ``#include<Python.h>``

and

    ``#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION``
    ``#include <numpy/arrayobject.h>``

are specific to the Python and Numpy APIs, respectively, and must be included in order to access the objects and functions that are used to pass data back and forth between the programming languages.

Wrapper
^^^^^^^

Overview
________

The wrapper is where those functions are defined, that will be called directly from Python. The intended role for these wrapper functions is to check the incoming Python data structures, and to create references to the relevant data using the Python API.

Ideally, this is done in such a way that the Python API is invoked only in the wrapper functions. In other words, the referenced data should be formatted so that it may be operated on directly by routines written purely in C. Since the Vortex-Lattice Method involves large arrays of data, this is especially important: copying or conversion of data would incur non-negligible computational costs.

The NumPy array format allows this, as it consists of a contiguous memory block (containing the actual data) and some metadata (size, shape, type, etc.). This is otherwise not true for most Python types, as these are really objects – even numbers! Therefore, the wrapper functions must rely more heavily on the API to convert these to C types.

Wrapper functions
_________________

Any wrapper function that is directly called from Python should look like:

.. code-block:: c

    static PyObject* py2c_lattice( PyObject *self, PyObject *args )
    {
        PyObject* py_myobject = NULL;
        PyArrayObject* py_myarray = NULL;

        if (!PyArg_ParseTuple(args, "OO!",
                    &py_myobject,
                    &PyArray_Type, &py_myarray ))
            return NULL;
    ...

Where ``PyObject*`` is the type of Python objects, and ``PyArrayObject*`` is the type of NumPy arrays. The pointers to these input data structures, chosen here as an object and an array, are first declared (here also initialized as ``NULL``).

Then, the API function ``PyArg_ParseTuple`` is invoked. This functions interprets the arguments received from Python. It must be provided with the expected types of the incoming data (denoted by characters, and concatenated in a string – ``"OO!"`` in our example), and with the previously declared pointers we wish to use to refer to each input.

The complete documentation on the ``PyArg_ParseTuple`` and its counterparts, as well as a description of the possible inputs, may be found here:

* https://docs.python.org/2/extending/extending.html
* https://docs.python.org/2/c-api/arg.html#c.PyArg_ParseTuple

The remaining code in the wrapper should be dedicated to checking the type, value, etc. of the incoming data using the API. It is important to ensure that the references one wishes to pass on to the C routines point to the correct data.

The full list of API functions, and a number of these functions of particular interest when checking and creating references to data in Python objects, may be found here:

* https://docs.python.org/2/c-api/index.html
* https://docs.python.org/2/c-api/concrete.html

..
    ===========================================================================

In |name|, the wrapper file ``c_vlm.cpp`` contains the code for interpreting Python input data in separate functions, one for each data structure. This way, if the data structure has been modified, the wrapper must be adapted only in one location. These functions are named ``get_*`` and ``set_*`` because they also create references to relevant data and give these references to the C structs used in the remaining C routines.

Once the referenced data has been checked and has been made readable as a C type, the wrapper function should call the actual C routine that operates on said data.

When finished, the wrapper function should return ``Py_None`` (Python's ``None`` - also an object!). Since we are creating this new Python object to return it to the caller, we must increase the reference count to this object by adding ``Py_INCREF(Py_None)`` before the return statement. I would recommend that the reader also reads the documentation on reference counting in extensions:

* https://docs.python.org/2/extending/extending.html#reference-counts

  However, even in the VLM extension of |name|, this aspect was not of concern and has not posed any problems.

Additional API requirements
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Because the wrapper functions are to be imported into Python, the wrapper file must be equipped with a number of additional functions and structured in a certain way, in order to behave as Python expects.

First, each of the wrapper functions should be given a docstring, a string containing a brief description of what it does. The wrapper “module”, or rather, the .cpp file, should also have a docstring. It is most convenient to define these strings as follows:

.. code-block:: c

    static char mymodule_docstr[] =
        "Contains C/C++ routines for doing things.\n";
    static char py2c_function_docstr[] =
        "Interfaces the C/C++ doing-of-things function with Python.\n";

Where ``mymodule`` is the name of the file, and ``py2c_function`` is the name of a wrapper function.

Next, each of the wrapper functions that is to be called directly from Python must be listed in the so-called method mapping table. This structure maps a name, docstring and argument format to each wrapper function. This makes the C wrapper function identifiable as a Python function.

.. code-block:: c

    static PyMethodDef mymoduleMethods[] = {
        	{ "py2c_function", py2c_function, METH_VARARGS, py2c_function_docstr},
    	...
        	{ NULL }
    };

The method mapping table is of type PyMethodDef and must be named ``*Methods``, where the asterisk must be replaced with the name of the dynamic library to be imported in Python. This is usually the same name as the wrapper file, although this is entirely dependent on how the files are compiled.

The table should be ended with ``{NULL}``.

The method mapping table should be followed by the so-called module initialization function, which is called when the Python code imports the C extension for the first time. This function has the following structure:

.. code-block:: c

    PyMODINIT_FUNC initmymodule ()
    {
        (void) Py_InitModule3( "mymodule", mymoduleMethods, mymodule_docstr );
        import_array();
    }

The initialization function should be named init*, where the asterisk must be replaced with the name of the dynamic library that is compiled from the C code and imported into Python. The initialization function maps the module to its name, its method mapping table and its docstring.

The statement import_array() is required for the NumPy API.

The documentation on the method mapping table and the initialization function is a very useful resource:

* https://docs.python.org/2.7/extending/extending.html#the-module-s-method-table-and-initialization-function

C routines
^^^^^^^^^^

The remaining ``.cpp`` files may contain functions independent on the Python-to-C API, so long as they operate on the Python data using the references created by the C wrapper.

