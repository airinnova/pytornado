############################################################
############################################################
############################################################
# ==> DEPRECATED METHOD
    # def get_point(self, coord_s, coord_c):
    #     """
    #     Returns X, Y, Z of point at local coordinates S, C.

    #     Args:
    #         :coord_s: (float) span- wise fraction of the quadrilateral
    #         :coord_c: (float) chord-wise fraction of the quadrilateral

    #     Returns:
    #         :point: (numpy) X, Y, Z-coordinates of point
    #     """

    #     if any(v for v in self.vertices.values() if v is None):
    #         raise ComponentDefinitionError("method 'get_point' requires vertices A, B, C, D.")

    #     alfa1 = self.vertices['a'][0]
    #     alfa2 = self.vertices['b'][0] - self.vertices['a'][0]
    #     alfa3 = self.vertices['d'][0] - self.vertices['a'][0]
    #     alfa4 = self.vertices['a'][0] - self.vertices['b'][0] + self.vertices['c'][0] - self.vertices['d'][0]

    #     beta1 = self.vertices['a'][1]
    #     beta2 = self.vertices['b'][1] - self.vertices['a'][1]
    #     beta3 = self.vertices['d'][1] - self.vertices['a'][1]
    #     beta4 = self.vertices['a'][1] - self.vertices['b'][1] + self.vertices['c'][1] - self.vertices['d'][1]

    #     gama1 = self.vertices['a'][2]
    #     gama2 = self.vertices['b'][2] - self.vertices['a'][2]
    #     gama3 = self.vertices['d'][2] - self.vertices['a'][2]
    #     gama4 = self.vertices['a'][2] - self.vertices['b'][2] + self.vertices['c'][2] - self.vertices['d'][2]

    #     x = alfa1 + alfa2*coord_s + alfa3*coord_c + alfa4*coord_s*coord_c
    #     y = beta1 + beta2*coord_s + beta3*coord_c + beta4*coord_s*coord_c
    #     z = gama1 + gama2*coord_s + gama3*coord_c + gama4*coord_s*coord_c

    #     return np.array([x, y, z])
############################################################
############################################################
############################################################


