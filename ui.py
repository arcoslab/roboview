# ui.py -- A VTK "Widget" for displaying robots
# -*- coding: utf-8 -*-
#
# Written by Jonathan Kleinehellefort <jk@molb.org>.
#
# Copyright 2008 Lehrstuhl Bildverstehen und wissensbasierte Systeme,
#                Technische Universität München
#
# This file is part of RoboView.
# 
# RoboView is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# RoboView is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details. You should have received a
# copy of the GNU General Public License along with PyPlayerCGen.  If
# not, see <http://www.gnu.org/licenses/>.

__all__ = ['RobotWidget']

from display import *
from math import pi, sqrt, acos, sin

arrow_size=0.05
basic_arrow = scale(arrow_size,arrow_size,arrow_size, arrow)
x_arrow = basic_arrow
y_arrow = rotate_z(pi/2, basic_arrow)
z_arrow = rotate_y(-pi/2, basic_arrow)
cylinder_size=0.02
cube_size=0.02
sphere_size=0.02
link_size=0.01
x_cylinder = scale(cylinder_size,cylinder_size, cylinder_size, rotate_z(pi/2, cylinder))
y_cylinder = scale(cylinder_size, cylinder_size, cylinder_size, cylinder)
z_cylinder = scale(cylinder_size, cylinder_size, cylinder_size, rotate_x(pi/2, cylinder))
hx_cylinder = scale(.5, 1, 1, x_cylinder)
joint_cube = scale(cube_size, cube_size, cube_size, cube)
transx_cylinder = scale(cylinder_size, .03, .03, translate(.5, 0, 0,
                                             rotate_z(pi/2, cylinder)))
link_cylinder = translate(0.5, 0, 0,
                          scale(1, link_size, link_size,
                                rotate_z(-pi/2, cylinder)))
ef_sphere = scale(sphere_size, sphere_size, sphere_size, sphere)

def vec_abs(v):
    x, y, z = v
    return sqrt(x*x + y*y + z*z)

def vec_smul(u, v):
    ux, uy, uz = u
    vx, vy, vz = v
    return ux*vx + uy*vy + uz*vz

def vec_xmul(u, v):
    ux, uy, uz = u
    vx, vy, vz = v
    return uy*vz - uz*vy, uz*vx - ux*vz, ux*vy - uy*vx

def vec_xmul_len(u, v):
    ret = vec_abs(u) * vec_abs(v) * sin(vec_ang(u, v) - pi/2)
    return ret

def vec_ang(u, v):
    if vec_abs(u) * vec_abs(v) == 0.0:
        return 0.0
    ret = acos(vec_smul(u, v) / (vec_abs(u) * vec_abs(v)))
    print 'ret', ret
    return ret

def vec_s(v, s):
    return [ve * s for ve in v]

def vec_add(u, v):
    return [ue + ve for ue, ve in zip(u, v)]

def vec_sub(u, v):
    return [ue - ve for ue, ve in zip(u, v)]

def matrix_x_dir(m):
    return m[0, 0], m[1, 0], m[2, 0]

def matrix_y_dir(m):
    return m[0, 1], m[1, 1], m[2, 1]

def matrix_z_dir(m):
    return m[0, 2], m[1, 2], m[2, 2]

def vec_from_matrix(m):
    return m.p[0], m.p[1], m.p[2]

def normalize(v):
    a = vec_abs(v)
    return v[0] / a, v[1] / a, v[2] / a

def make_vector_x_base(m, v):
    '''Make v the base of the x axis in matrix m.'''
    if v[1] == 0 and v[2] == 0:
        w = (0, 1, 0)
        u = (0, 0, 1)
    else:
        w = normalize((0, -v[2], v[1]))
        u = normalize((v[1]**2 + v[2]**2, v[0] * v[1], -v[0] * v[2]))
    m[0, 0] = v[0]
    m[1, 0] = v[1]
    m[2, 0] = v[2]
    m[0, 1] = w[0]
    m[1, 1] = w[1]
    m[2, 1] = w[2]
    m[0, 2] = u[0]
    m[1, 2] = u[1]
    m[2, 2] = u[2]

def make_link_cylinder(joint):
    frame = joint.static_transform.Inverse()
    link_frame = MatrixTransform()
    make_vector_x_base(link_frame, vec_from_matrix(frame))
    return link_frame(link_cylinder)

class JointWidget(object):

    def __init__(self, frame, joint=None, type='rot_z'):
        self.frame = frame
        self.joint = joint
        self.rotate_handler = lambda x: None
        self.type = type

    def add_to(self, display):
        t = self.frame
        display.add(id(self), t(x_arrow), color=(1, 0, 0))
        display.add(id(self), t(y_arrow), color=(0, 1, 0))
        display.add(id(self), t(z_arrow), color=(0, 0, 1))
        display.add(id(self), t({'rot_x': x_cylinder,
                                 'rot_y': y_cylinder,
                                 'rot_z': z_cylinder}[self.type]))
        if self.joint is not None:
            display.add(None, t(make_link_cylinder(self.joint)), opacity=.3)
        def handle_button_press(*args):
            display.enable(id(self))
        display.register(None, id(self), 'button-press', handle_button_press)
        def handle_button_release(*args):
            display.enable(None)
        display.register(id(self), None, 'button-release',
                         handle_button_release)
        def handle_move(dx, dy, dv, dr):
            e = {'rot_x': matrix_x_dir,
                 'rot_y': matrix_y_dir,
                 'rot_z': matrix_z_dir}[self.type](self.frame)
            self.rotate_handler(vec_smul(dr, e))
        display.register(id(self), None, 'move', handle_move)

    def update(self, frame, value):
        for i, j in [(i, j) for i in range(4) for j in range(4)]:
            self.frame[i, j] = frame[i, j]

class TransJointWidget(object):

    def __init__(self, frame, joint=None, type='trans_z'):
        self.frame = frame
        self.joint = joint
        self.rotate_handler = lambda x: None
        self.type = type
        self.len_frame = MatrixTransform()

    def add_to(self, display):
        dir = {'trans_x': lambda n: n,
             'trans_y': lambda n: rotate_z(pi/2, n),
             'trans_z': lambda n: rotate_y(-pi/2, n)}[self.type]
        t = self.frame
        display.add(id(self), t(x_arrow), color=(1, 0, 0))
        display.add(id(self), t(y_arrow), color=(0, 1, 0))
        display.add(id(self), t(z_arrow), color=(0, 0, 1))
        display.add(id(self), t(dir(hx_cylinder)))
        display.add(id(self), t(dir(translate(-1/40.0, 0, 0, self.len_frame(transx_cylinder)))))
        if self.joint is not None:
            display.add(None, t(make_link_cylinder(self.joint)), opacity=.3)
        def handle_button_press(*args):
            display.enable(id(self))
        display.register(None, id(self), 'button-press', handle_button_press)
        def handle_button_release(*args):
            display.enable(None)
        display.register(id(self), None, 'button-release',
                         handle_button_release)
        def handle_move(dx, dy, dv, dr):
            e = {'trans_x': matrix_x_dir,
                 'trans_y': matrix_y_dir,
                 'trans_z': matrix_z_dir}[self.type](self.frame)
            self.rotate_handler(-.3 * vec_smul(dv, e))
        display.register(id(self), None, 'move', handle_move)

    def update(self, frame, value):
        for i, j in [(i, j) for i in range(4) for j in range(4)]:
            self.frame[i, j] = frame[i, j]
        self.len_frame[0, 0] = 20 * value + 1

class NoneJointWidget(object):

    def __init__(self, frame, joint=None):
        self.frame = frame
        self.joint = joint

    def add_to(self, display):
        t = self.frame
        display.add(id(self), t(x_arrow), color=(1, 0, 0))
        display.add(id(self), t(y_arrow), color=(0, 1, 0))
        display.add(id(self), t(z_arrow), color=(0, 0, 1))
        display.add(id(self), t(joint_cube))
        if self.joint is not None:
            display.add(None, t(make_link_cylinder(self.joint)), opacity=.3)

    def update(self, frame, value):
        for i, j in [(i, j) for i in range(4) for j in range(4)]:
            self.frame[i, j] = frame[i, j]

class EndEffectorWidget(object):

    def __init__(self, frame, joint=None):
        self.frame = frame
        self.joint = joint
        self.rotate_handler = lambda x: None

    def add_to(self, display):
        t = self.frame
        display.add(id(self), t(x_arrow), color=(1, 0, 0))
        display.add(id(self), t(y_arrow), color=(0, 1, 0))
        display.add(id(self), t(z_arrow), color=(0, 0, 1))
        display.add(id(self), t(ef_sphere))
        if self.joint is not None:
            display.add(None, t(make_link_cylinder(self.joint)), opacity=.3)
        def handle_button_press(x, y, n):
            if n == 1:
                display.enable((id(self), 'rotating'))
            elif n == 2:
                display.enable((id(self), 'translating'))
        display.register(None, id(self), 'button-press', handle_button_press)
        def handle_button_release(*args):
            display.enable(None)
        display.register((id(self), 'rotating'), None, 'button-release',
                         handle_button_release)
        display.register((id(self), 'translating'), None, 'button-release',
                         handle_button_release)
        def handle_translate(dx, dy, dv, dr):
            self.translate_handler(dv)
        display.register((id(self), 'translating'), None, 'move',
                         handle_translate)
        def handle_rotate(dx, dy, dv, dr):
            self.rotate_handler(dr)
        display.register((id(self), 'rotating'), None, 'move', handle_rotate)

    def update(self, frame):
        for i, j in [(i, j) for i in range(4) for j in range(4)]:
            self.frame[i, j] = frame[i, j]

class RobotWidget(object):

    def __init__(self, robot):
        self.joint_widgets = []
        joints = [j for j in robot]
        for j_prev, j in zip([None] + joints[:-1], joints):
            if j.type == 'none':
                self.joint_widgets.append(NoneJointWidget(MatrixTransform(), j_prev))
            elif j.type in ('rot_x', 'rot_y', 'rot_z'):
                self.joint_widgets.append(JointWidget(MatrixTransform(),
                                                      j_prev, j.type))
            else:
                self.joint_widgets.append(TransJointWidget(MatrixTransform(),
                                                      j_prev, j.type))
        self.ef_widget = EndEffectorWidget(MatrixTransform(), joints[-1])

    def add_to(self, display):
        for widget in self.joint_widgets:
            widget.add_to(display)
        self.ef_widget.add_to(display)

    def update(self, frames):
        for f, widget in zip(frames, self.joint_widgets + [self.ef_widget]):
            widget.update(f)
