Introduction
============

.. note::

    This summary is based/copied from [Dettmann2019]_ with the authors permission.

The vortex-lattice method (VLM) is the simplest general 3D potential flow model [Drela2014]_. Since the model is relatively easy to setup and has low computational cost, it is a widely used tool in conceptual aircraft design [Drela2014]_ [Seywald2016]. The theory is well covered in literature, for instance by Drela [Drela2014]_, Katz and Plotkin [Katz2001]_ and Bertin and Cummings [Bertin2014]_. Only a basic summary will be given here. The VLM makes use of many assumptions and simplifications. Most significantly, quasi-steady, *potential flow* is assumed. A potential flow implies an inviscid and irrotational flow field. Viscous, dissipative effects such as turbulence or the boundary layer cannot be resolved. Only induced drag can be computed. The flow field is further assumed to incompressible, which is a reasonable simplification in low subsonic airflow [Drela2014]_. The lifting surfaces are assumed to be thin. Small angles of attack and sideslip angles are assumed. In general, large-angle effects like stall cannot be modelled.

.. figure:: _static/images/vlm_discretisation.svg
   :width: 400 px
   :align: center
   :alt: VLM discretisation

   Concept of the VLM discretisation (adapted from [Drela2014]_). The shown lifting surface is divided into nine panels. A three-legged horseshoe vortex is placed on each panel.

The VLM is a numerical solution method for the general 3D *lifting surface problem* [Drela2014]_. The lifting surface problem is a model in which lifting surfaces and the wake are represented by infinitely thin vortex sheets with a sheet strength distribution [Drela2014]_. The potential flow field around the lifting surfaces is influenced by these vortex sheets. The basic approach applied in the VLM is to discretise the continuous vortex sheet strength distribution. To achieve this, each lifting surface (modelled as a flat sheet) is divided into small quadrilateral panels (see figure above), together constituting a mesh (or lattice). The distributed vortex distribution is then lumped into so-called horseshoe vortices. On each panel a horseshoe vortex with three legs is placed. A bound leg, modelling the lifting properties, lies at the panel quarter chord line. Two trailing legs, which model the influence of the wake, extend from the ends of the bound leg parallel to the freestream direction to downstream infinity [#]_. Each leg of the same horseshoe vortex i has the same circulation strength :math:`\Gamma_i` (see figure below).

.. [#] The horseshoe vortex geometry is not consistently defined in literature and in different VLM implementations. Katz and Plotkin [Katz2001]_ include the most elaborate explanation and mention three different variations. Differently defined horseshoe vortex geometries can cause differences in between results provided by different VLM implementations.

.. figure:: _static/images/horseshoe_vortex_geometry.svg
   :width: 450 px
   :align: center
   :alt: Horseshoe vortex geometry

   Horseshoe vortex geometry and variables involved in the Kutta-Joukowski theorem (adapted from [Drela2014]_)

Every horseshoe vortex will induce some velocity contribution at any field point :math:`\mathbf{r}`. This induced velocity is computed using the Biot-Savart law, analogous to an electric current inducing a magnetic field. The total flow field velocity :math:`\mathbf{V}(\mathbf{r})` relative to the aircraft's body-fixed axes at a position r is a result of the freestream velocity, the aircraft's rotation rate and the contribution of all horseshoe vortices. This concept is used to set up a system of linear equations by applying a flow tangency boundary condition. At control points (also known as collocation points) located at :math:`\mathbf{r}_\text{c i}` on a panel :math:`i` (centre of the panel three-quarter chord line), the flow in the direction of the panel's normal vector [#]_ :math:`\mathbf{n}_i` is prescribed to be zero, :math:`\mathbf{V}(\mathbf{r}_\text{c i}) * \mathbf{n}_i = 0`, where :math:`\mathbf{V}(\mathbf{r}_\text{c i})` is the velocity vector at the control point given as a results of induced and freestream velocity as well as the aircraft's rotation rate. The boundary condition implies that there cannot be airflow through the wing surface at this point.

.. [#] The normal vector does not have to be the geometric normal of the panel. It may be rotated in order to model control surface deflections or aerofoils [Drela2014]_.

The equations enforcing the flow tangency boundary conditions on :math:`N` panels can be assembled into a linear system of equations for the unknown vortex strength :math:`\Gamma_i`. The matrix formulation of the :math:`N \times N` system has the form

.. math::

    \begin{align}
        %% SEE https://en.wikipedia.org/wiki/Vortex_lattice_method
        \label{eq:vlm_sys_of_eq}
        \begin{bmatrix}
            a_{11} & a_{12} & \dots & a_\text{1n} \\
            a_\text{21} & \ddots & & \vdots \\
            \vdots & & \ddots & \vdots \\
            a_\text{n1} & a_\text{n2} & \dots & a_\text{nn}
        \end{bmatrix}
        \cdot
        \begin{pmatrix}
            \Gamma_1 \\
            \Gamma_2 \\
            \vdots \\
            \Gamma_\text{n}
        \end{pmatrix}
            =
        \begin{pmatrix}
            b_{1} \\
            b_{2} \\
            \vdots \\
            b_\text{n}
        \end{pmatrix}
    \end{align}

where the :math:`a_{ij}` denote the elements of a so-called aerodynamic influence coefficient matrix, and :math:`\Gamma_{i}` is the circulation of a panel :math:`i`. The :math:`b_i` on the right-hand side are functions of the freestream velocity, the aircraft rotation rate and the panel normal vectors. The :math:`a_{ij}` and :math:`b_{i}` only depend on the geometry and the flight state and are hence known beforehand. Equation (2.1) can be solved to obtain the horseshoe vortex strength :math:`\Gamma_i` (circulation) for each panel :math:`i`. With known circulation, the aerodynamic force :math:`\mathbf{F}_i` acting at the quarter chord midpoint of a panel can be computed using the *Kutta-Joukowski theorem*,

.. math::

    \mathbf{F}_i = \varrho_\text{air} \cdot \mathbf{V}_i \times \mathbf{s}_i \cdot \Gamma_i

where :math:`\varrho_\text{air}` is the air density, :math:`\mathbf{V}_i` the velocity relative to the horseshoe vortex bound leg midpoint, and :math:`\mathbf{s}_i = \mathbf{r_b} - \mathbf{r_a}` a is the vector of the bound leg (see figure above). Based on the computed force distribution, aerodynamic parameters such as lift and (induced) drag coefficients can be obtained. For all further aeroelastic analyses, the panel forces are considered to be the main result of the VLM. Practically, these forces represent a discretised formulation of the continuous pressure distribution over the lifting surfaces.
