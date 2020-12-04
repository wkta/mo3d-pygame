import math

import numpy as np
import pygame


"""
in this file we define all classes useful for 3d rendering,
or dedicated data structures (Mesh, PointCloud) related to geometry.

In the long run, we could use this foundation for rendering not only flat objects,
 but also meshes created by Blender or another 3d-modeling software.
"""


class Quaternion:
    """
    Tom was here
    """

    def __init__(self, x, y, z, aleph):
        self.np_arr = np.array([x, y, z, aleph])

    @property
    def x(self):
        return self.np_arr[0]

    @property
    def y(self):
        return self.np_arr[1]

    @property
    def z(self):
        return self.np_arr[2]

    @property
    def aleph(self):
        return self.np_arr[3]

    def __str__(self):
        return '({}, {}, {}, {})'.format(self.x, self.y, self.z, self.aleph)


class Camera:
    def __init__(self, pos3d, angle_horz, angle_vert):
        # Camera position and rotation in space
        self.position = list(pos3d)
        self.angle_aroundx = angle_horz
        self.angle_aroundy = angle_vert

    def get_infos(self):
        return self.position[0], self.position[1], self.position[2], self.angle_aroundx, self.angle_aroundy

    def addToPosition(self, vect3):
        for i in range(3):
            self.position[i] += vect3[i]

    def addToAngleHorz(self, val):
        self.angle_aroundx += val

    def addToAngleVert(self, val):
        self.angle_aroundy += val


class ThreeDeeSkeleton:
    """
    point set + lines
    """
    def __init__(self, pt_list: list, pt_pairs: set):
        self._pt_set = pt_list
        self.vertices = list()
        for p in pt_list:
            self.vertices.append(Quaternion(p[0], p[1], p[2], 1))
        self._pt_pairs = pt_pairs

    @staticmethod
    def rotate2d(pos, rad):
        x, y = pos
        s, c = math.sin(rad), math.cos(rad)
        return x * c - y * s, y * c + x * s

    def mesh_translate(self, dx, dy, dz):
        for k in range(len(self.vertices)):
            x, y, z, mu = self.vertices[k].np_arr
            x += dx
            y += dy
            z += dz
            self.vertices[k] = Quaternion(x, y, z, 1)

    def mesh_rotate(self, radiansx, radiansy, radiansz, refpt=None):

        rsinx = math.sin(radiansx)
        rcosx = math.cos(radiansx)

        rsiny = math.sin(radiansy)
        rcosy = math.cos(radiansy)

        rsinz = math.sin(radiansz)
        rcosz = math.cos(radiansz)

        # rot matrix around X axis
        rx_matrix = np.array([[rcosx, 0., rsinx, 0.],
                            [0., 1, 0., 0.],
                            [-rsinx, 0., rcosx, 0.],
                            [0., 0., 0., 1.]])
        # rot matrix around Y axis
        ry_matrix = np.array([[1, 0., 0, 0.],
                            [0., rcosy, -rsiny, 0.],
                            [0, rsiny, rcosy, 0.],
                            [0., 0., 0., 1.]])
        # rot matrix around Z axis
        rz_matrix = np.array([[rcosz, -rsinz, 0, 0.],
                            [rsinz, rcosz, 0, 0.],
                            [0, 0, 1, 0.],
                            [0., 0., 0., 1.]])
        for vert in self.vertices:
            if refpt is not None:
                temp = refpt
                vert.np_arr = (vert.np_arr - temp).dot(rx_matrix.dot(ry_matrix).dot(rz_matrix))
                vert.np_arr += temp
            else:
                vert.np_arr = vert.np_arr.dot(rx_matrix.dot(ry_matrix).dot(rz_matrix))

    def render(self, pygame_surface, cam, color):
        # projection
        li_2d_points = list()
        pt_sizes = list()
        for pt3d in self.vertices:
            x, y, z, mu = pt3d.np_arr
            # x, y, z = vert[0], vert[1], vert[2]

            x -= cam.position[0]
            y -= cam.position[1]
            z -= cam.position[2]

            x, y = ThreeDeeSkeleton.rotate2d((x, y), cam.angle_aroundx)
            y, z = ThreeDeeSkeleton.rotate2d((y, z), cam.angle_aroundy)
            f = 500 / z

            ex, ey = x * f, y * f
            li_2d_points.append(
                (int(ex) + int(pygame_surface.get_width() / 2), int(ey) + int(pygame_surface.get_height() / 2))
            )
            # estimating a dot size w.r.t. camera pos-based depth
            s = int(2 / (cam.position[2] - z) * 40)
            if s < 2:
                s = 2
            pt_sizes.append(s)

        # - We draw dots

        # -- mapping to viewport
        li_scr_points = list()
        for pt2d in li_2d_points:
            scrx = int(pt2d[0]) + int(pygame_surface.get_width() / 2)
            scry = int(pt2d[1]) + int(pygame_surface.get_height() / 2)
            li_scr_points.append((scrx, scry))

        for k, pt in enumerate(li_scr_points):

            pygame.draw.circle(
                pygame_surface,
                color,
                (pt[0], pt[1]),
                pt_sizes[k]
            )

        # -- lets draw lines
        # --- forcing red color
        mycolor = (255, 0, 0)  # flashy red
        for ptpair in self._pt_pairs:
            pt_a = li_scr_points[ptpair[0]]
            pt_b = li_scr_points[ptpair[1]]
            pygame.draw.line(pygame_surface, mycolor, pt_a, pt_b, 2)


class Mesh:

    #  how to render? 1 - full, 2 - circles only
    FULL_RENDER_TYPE, DOTS_RENDER_TYPE = 1, 2

    def __init__(self, name, verts_count, edges, faces, colors, rtype):
        self.name = name
        self.vertices = [np.array([0., 0., 0., 0.])] * verts_count
        self.edges = edges
        self.faces = faces
        self.colors = colors
        assert rtype in (self.FULL_RENDER_TYPE, self.DOTS_RENDER_TYPE)
        self.rtype = rtype
        print("Mesh created:", self.name)

    def __repr__(self):
        return self.name

    def getz_order(self):  # useful for sorting mesh w.r.t. relative depth camera<>mesh
        sumz = 0
        for vertex in self.vertices:
            sumz += vertex.retz()

        return sumz

    def scale(self, x, y, z):
        s_matrix = np.array([[x, 0., 0., 0.],
                            [0., y, 0., 0.],
                            [0., 0., z, 0.],
                            [0., 0., 0., 1.]])

        for vert in self.vertices:
            vert.vector = vert.vector.dot(s_matrix)

        return s_matrix

    def rotate(self, radiansx, radiansy, radiansz):

        rsinx = math.sin(radiansx)
        rcosx = math.cos(radiansx)

        rsiny = math.sin(radiansy)
        rcosy = math.cos(radiansy)

        rsinz = math.sin(radiansz)
        rcosz = math.cos(radiansz)

        # Rotation Matrix around X axis
        rx_matrix = np.array([[rcosx, 0., rsinx, 0.],
                            [0., 1, 0., 0.],
                            [-rsinx, 0., rcosx, 0.],
                            [0., 0., 0., 1.]])
        # Rotation Matrix around Y axis
        ry_matrix = np.array([[1, 0., 0, 0.],
                            [0., rcosy, -rsiny, 0.],
                            [0, rsiny, rcosy, 0.],
                            [0., 0., 0., 1.]])
        # Rotation Matrix around Z axis
        rz_matrix = np.array([[rcosz, -rsinz, 0, 0.],
                            [rsinz, rcosz, 0, 0.],
                            [0, 0, 1, 0.],
                            [0., 0., 0., 1.]])
        for vert in self.vertices:
            vert.vector = vert.vector.dot(rx_matrix.dot(ry_matrix).dot(rz_matrix))

        return rx_matrix

    def translate(self, x, y, z):
        t_matrix = np.array([[1., 0., 0., x],
                            [0., 1., 0., y],
                            [0., 0., 1., z],
                            [0., 0., 0., 1.]])

        for vert in self.vertices:
            vert.vector = t_matrix.dot(vert.vector)

        return t_matrix

    def rotate2d(self, pos, rad):
        x, y = pos
        s, c = math.sin(rad), math.cos(rad)
        return x * c - y * s, y * c + x * s

    def render(self, surface, cam, color):
        if self.rtype == 2:
            self._draw_dots(surface, cam, color)
        else:
            self._draw_polygons(surface, cam, color)

    def _draw_dots(self, surface, cam, color):
        calculated = False

        for vert in self.vertices:

            x, y, z = vert.x, vert.y, vert.z
            x -= cam.position[0]
            y -= cam.position[1]
            z -= cam.position[2]

            x, y = self.rotate2d((x, y), cam.angle_aroundx)
            y, z = self.rotate2d((y, z), cam.angle_aroundy)
            f = 500 / z

            ex, ey = x * f, y * f

            # TODO: Make it as point counting routine
            if int(cam.position[2]) == int(vert.z) and not calculated:
                # print(int(cam.position[2]), vert.vector[2])
                calculated = True

            # if cam.position[2] <= vert.z:
            pygame.draw.circle(surface, color, (
            int(ex) + int(surface.get_width() / 2), int(ey) + int(surface.get_height() / 2)),
                               int(2 / (cam.position[2] - vert.z) * 40))

    def _draw_polygons(self, surface, cam, color):
        vert_list = []
        # Or we draw shapes
        points = []

        for vert in self.vertices:
            x, y, z = vert.x, vert.y, vert.z
            x -= cam.position[0]
            y -= cam.position[1]
            z -= cam.position[2]

            vert_list += [(x, y, z)]
            x, y = self.rotate2d((x, y), cam.angle_aroundx)
            y, z = self.rotate2d((y, z), cam.angle_aroundy)
            f = 500 / z

            ex, ey = x * f, y * f
            points += [(int(ex) + int(surface.get_width() / 2), int(ey) + int(surface.get_height() / 2))]

        face_list = []
        face_color = []
        depth = []

        for f in range(len(self.faces)):
            face = self.faces[f]
            for i in face:
                coords = [points[i] for i in face]
                face_list += [coords]
                face_color += [self.colors[f]]
                depth += [sum(sum(vert_list[j][i] for j in face)**2 for i in range(3))]

        order = sorted(range(len(face_list)), key=lambda i:depth[i], reverse=True)

        for i in order:
            if cam.position[2] > vert.z:
                try:
                    pygame.draw.polygon(surface, face_color[i], face_list[i])
                except:
                    pass


def render_all_meshes(meshes, camera, surf):
    color = (255, 255, 0)
    for mesh in meshes:
        mesh.render(surf, camera, color)
