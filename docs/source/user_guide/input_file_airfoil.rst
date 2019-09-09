.. _input_file_airfoils:

Airfoil files
=============

Arbitrary airfoil geometries can be modelled in |name|. How airfoils files are referenced and used is described in :ref:`input_file_aircraft`. This page gives more notes on the actual airfoil file *format*.

.. figure:: ../_static/images/airfoil_nomenclature.svg
    :width: 600 px
    :align: center
    :alt: Example

    Airfoil nomenclature. Image in the public domain, via `Wikimedia Commons <https://commons.wikimedia.org/wiki/File:Wing_profile_nomenclature.svg>`_.

Files found in the `UIUC Airfoil Coordinates Database <https://m-selig.ae.illinois.edu/ads/coord_database.html>`_ can be loaded. You can download a file from the UIUC database, place it in the *airfoils* folder and then reference it via ``airfoils/downloaded_airfoil_file.dat`` (see :ref:`input_file_aircraft`).

Formats
-------

Two different formats can be read. Examples are shown below. Note that more information can be found here: `UIUC Airfoil Coordinates Database <https://m-selig.ae.illinois.edu/ads/coord_database.html>`_

Example format a
----------------

* First row is name of airfoil or comment
* Two columns for :math:`x`- and :math:`y`-coordinates
* Data typically starts at :math:`x = 1`

.. code::

    AIRFOIL NAME
    1.00      0.00
    0.80      0.05
    0.60      0.10
    0.40      0.10
    0.20      0.05
    0.00     -0.01
    0.20     -0.05
    0.40     -0.10
    0.60     -0.10
    0.80     -0.10
    1.00     -0.00


Example format b
----------------

* First row is name of airfoil or comment
* Second row contains two columns with integers for the *number* of upper and lower  :math:`x`, :math:`y` coordinates, respectively
* Then, there are two blocks of :math:`x`-, and :math:`y`-coordinates:

    * The first one for the upper points
    * The second one for the lower points

.. code::

    AIRFOIL NAME
    43.     41.

    0.00   0.00
    0.00   0.00
    0.00   0.00
    0.00   0.00
    0.00   0.00
    0.00   0.01
    0.00   0.01
    0.00   0.01
    0.01   0.01
    0.01   0.01
    0.01   0.02
    0.02   0.02
    0.03   0.02
    0.04   0.03
    0.05   0.03
    0.06   0.03
    0.08   0.04
    0.11   0.04
    0.15   0.04
    0.20   0.05
    0.25   0.05
    0.30   0.05
    0.35   0.05
    0.40   0.05
    0.45   0.04
    0.50   0.04
    0.55   0.04
    0.60   0.04
    0.65   0.03
    0.69   0.03
    0.73   0.02
    0.77   0.02
    0.81   0.02
    0.84   0.01
    0.88   0.01
    0.91   0.00
    0.93   0.00
    0.95   0.00
    0.97   0.00
    0.98   0.00
    0.99   0.00
    0.99   0.00
    1.00   0.00

    0.00   0.00
    0.00   -.00
    0.00   -.00
    0.00   -.00
    0.00   -.00
    0.00   -.00
    0.01   -.00
    0.01   -.01
    0.01   -.01
    0.02   -.01
    0.03   -.01
    0.04   -.01
    0.05   -.01
    0.07   -.01
    0.09   -.01
    0.11   -.02
    0.15   -.02
    0.20   -.02
    0.25   -.02
    0.30   -.02
    0.35   -.02
    0.40   -.02
    0.45   -.02
    0.50   -.02
    0.55   -.02
    0.60   -.02
    0.65   -.02
    0.69   -.02
    0.73   -.02
    0.77   -.02
    0.81   -.01
    0.84   -.01
    0.88   -.01
    0.91   -.01
    0.93   -.00
    0.95   -.00
    0.97   -.00
    0.98   -.00
    0.99   -.00
    0.99   -.00
    1.00   -.00

.. seealso::

    |name| uses the *airfoils* library to load and model airfoils.

    * https://github.com/airinnova/airfoils
