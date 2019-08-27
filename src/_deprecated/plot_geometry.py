
# FROM plot.geometry
# - Function is not being used anywhere

def view_overlay(aircraft1, aircraft2, plt_settings, block=True):
    """
    Generate 3D overlaid view of two aircraft geometries.

    By default, shows segment vertices and edges.

    Args:
        :aircraft1: (object) data structure for the first aircraft
        :aircraft2: (object) data structure for the second aircraft
        :block: (bool) halt execution while figure is open
    """

    logger.info("Generating geometry overlay plot...")

    if not aircraft1.state:
        logger.warning("Aircraft1 is ill-defined!")

    if not aircraft2.state:
        logger.warning("Aircraft2 is ill-defined!")

    # 2. 3D VIEW ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    figure_1 = plt.figure(figsize=(12, 12), edgecolor=COLOR1)
    axes_xyz = figure_1.add_subplot(111, projection='3d')
    axes_xyz.set_aspect('equal')

    figure_2 = plt.figure(figsize=(20, 6), edgecolor=COLOR1)
    axes_yz = figure_2.add_subplot(131)
    axes_xz = figure_2.add_subplot(132)
    axes_xy = figure_2.add_subplot(133)

    axes_yz.set_aspect('equal')
    axes_xz.set_aspect('equal')
    axes_xy.set_aspect('equal')

    # 2.1. DISPLAY GEOMETRY ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    lims = np.zeros((2, 3))

    for aircraft, color in zip([aircraft1, aircraft2], [COLOR1, COLOR2]):
        for wing in aircraft.wing.values():
            for segment in wing.segment.values():
                points = np.array([segment.vertices['a'],
                                   segment.vertices['b'],
                                   segment.vertices['c'],
                                   segment.vertices['d'],
                                   segment.vertices['a']])

                X = points[:, 0]
                Y = points[:, 1]
                Z = points[:, 2]

                get_limits(points, lims, symm=wing.symmetry)
                axes_xyz.plot(X, Y, Z, color=color, marker='.', markersize=4)

                axes_yz.plot(Y, Z, color=color, marker='.', markersize=4)
                axes_xz.plot(X, Z, color=color, marker='.', markersize=4)
                axes_xy.plot(X, Y, color=color, marker='.', markersize=4)

                # x, y-symmetry
                if wing.symmetry == 1:
                    axes_xyz.plot(X, Y, -Z, color=color, linestyle=':', marker='.', markersize=2)
                    axes_yz.plot(Y, -Z, color=color, linestyle=':', marker='.', markersize=2)
                    axes_xz.plot(X, -Z, color=color, linestyle=':', marker='.', markersize=2)

                # x, z-symmetry
                elif wing.symmetry == 2:
                    axes_xyz.plot(X, -Y, Z, color=color, linestyle=':', marker='.', markersize=2)
                    axes_yz.plot(-Y, Z, color=color, linestyle=':', marker='.', markersize=2)
                    axes_xy.plot(X, -Y, color=color, linestyle=':', marker='.', markersize=2)

                # y, z-symmetry
                elif wing.symmetry == 3:
                    axes_xyz.plot(-X, Y, Z, color=color, linestyle=':', marker='.', markersize=2)
                    axes_xz.plot(-X, Z, color=color, linestyle=':', marker='.', markersize=2)
                    axes_xy.plot(-X, Y, color=color, linestyle=':', marker='.', markersize=2)

    scale_fig(axes_xyz, lims)
    scale_fig(axes_yz, lims, directions='yz')
    scale_fig(axes_xz, lims, directions='xz')
    scale_fig(axes_xy, lims, directions='xy')

    # 2.2. DISPLAY ANNOTATIONS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    axes_xyz.annotate(f"aircraft 1 = {aircraft2.uid}\n"
                      + f"aircraft 2 = {aircraft1.uid}\n",
                      xy=(0, 0), xytext=(1, 0), textcoords='axes fraction', va='bottom', ha='right')

    # display additional information

    # 2.3. DISPLAY LABELS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    axes_xyz.set_xlabel('x [m]')
    axes_xyz.set_ylabel('y [m]')
    axes_xyz.set_zlabel('z [m]')

    axes_yz.set_xlabel('x [m]')
    axes_yz.set_ylabel('y [m]')

    axes_xz.set_xlabel('x [m]')
    axes_xz.set_ylabel('z [m]')

    axes_xy.set_xlabel('y [m]')
    axes_xy.set_ylabel('z [m]')

    axes_xyz.set_title("{} | {}".format(aircraft1.uid, aircraft2.uid))

    axes_yz.set_title("YZ")
    axes_xz.set_title("XZ")
    axes_xy.set_title("XY")

    figure_2.suptitle("{} | {}".format(aircraft1.uid, aircraft2.uid))

    plt.tight_layout()

    if plt_settings['save']:
        fname1 = os.path.join(plt_settings['plot_dir'], f"geo_overlay3D_{get_date_str()}.png")
        logger.info(f"Saving plot as file: '{truncate_filepath(fname1)}'")
        figure_1.savefig(fname1, dpi=300)

        fname2 = os.path.join(plt_settings['plot_dir'], f"geo_overlay_{get_date_str()}.png")
        logger.info(f"Saving plot as file: '{truncate_filepath(fname2)}'")
        figure_2.savefig(fname2, dpi=300)

    if plt_settings['show']:
        plt.show(block=block)

    plt.close('all')



