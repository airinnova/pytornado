.. _coeffs:

Loads and coefficients
======================

|name| computes different *global* force and moment coefficients. The definitions are described below. Notice that there are three different **reference values**:

* :math:`S` : Reference area
* :math:`c` : Reference chord
* :math:`b` : Reference span

There are two sets of *force* coefficients, the fist being described in the *body-fixed* system and the second being described in the *aerodynamic system* (see also :ref:`coordinate_systems`). The global force coefficients :math:`C_X`, :math:`C_Y`, :math:`C_Z` in the body-fixed system are defined as

.. math::
    C_X = \frac{F_x}{q \cdot S} \\
    C_Y = \frac{F_y}{q \cdot S} \\
    C_Z = \frac{F_z}{q \cdot S}

where :math:`F_x`, :math:`F_y` and :math:`F_z` are global forces in :math:`X`, :math:`Y` and :math:`Z` directions, respectively, :math:`q` is the dynamic pressure. Global lift, drag and side force coefficients (:math:`C_L`, :math:`C_D`, :math:`C_C`) describe forces in the aerodynamic coordinate system and are defined as

.. math::
    C_L = \frac{F_L}{q \cdot S} \\
    C_D = \frac{F_D}{q \cdot S} \\
    C_C = \frac{F_C}{q \cdot S}

where :math:`F_L`, :math:`F_D` and :math:`F_C` are global lift, drag and side force (in *Newtons*) in the aerodynamic system. Moment coefficients are defined with respect to the body-fixed system as

.. math::
    C_l = \frac{M_x}{q \cdot S \cdot b} \\
    C_m = \frac{M_y}{q \cdot S \cdot c} \\
    C_n = \frac{M_z}{q \cdot S \cdot b}

where :math:`M_x`, :math:`M_y` and :math:`M_z` are global moments about the in :math:`X`, :math:`Y` and :math:`Z` directions, respectively.

**TODO** explain ``gcenter`` and ``rcenter``
