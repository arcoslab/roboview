# display.py -- graphical vtk helper stuff
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

__all__ = ['Display', 'MatrixTransform', 'rotate_x', 'rotate_y', 'rotate_z',
           'scale', 'translate', 'arrow', 'cylinder', 'sphere', 'cube']

from vtk import *
from math import pi
import gtk
import gtkvtk

def vec_abs(v):
    x, y, z = v
    return sqrt(x*x + y*y + z*z)

def vec_smul(u, v):
    ux, uy, uz = u
    vx, vy, vz = v
    return ux*vx, uy*vy, uz*vz

def vec_xmul(u, v):
    ux, uy, uz = u
    vx, vy, vz = v
    return uy*vz - uz*vy, uz*vx - ux*vz, ux*vy - uy*vx

def vec_s(v, s):
    return [ve * s for ve in v]

def vec_add(u, v):
    return [ue + ve for ue, ve in zip(u, v)]

def vec_sub(u, v):
    return [ue - ve for ue, ve in zip(u, v)]

def pan_dist(cam, obj, foc):
    x, y, z = [(c - o) * (c - f) for c, o, f in zip(cam, obj, foc)]
    return sqrt(x*x + y*y + z*z)

def pan_scale(dist, fov):
    return fov * dist # estimation

class EventDispatcher(object):

    def __init__(self):
        self.state = None
        self.callbacks = {}

    def register(self, state, context, event, callback):
        self.callbacks.setdefault((state, context, event), []).append(callback)

    def enable(self, state):
        self.state = state

    def handle(self, context, event, *args, **kwargs):
        for callback in self.callbacks.get((self.state, context, event), []):
            callback(*args, **kwargs)

class Display(object):

    def __init__(self):
        self.ren = vtkRenderer()
        self.ren.SetBackground(1, 1, 1)
        self.ui_win = gtk.Window()
        self.ui_win.set_size_request(500, 500)
        self.view = gtkvtk.VtkRenderArea()
        self.ui_win.add(self.view)
        self.view.show()
        self.view.render_window.AddRenderer(self.ren)
        self.ui_win.connect('destroy', gtk.main_quit)
        self.win = self.view.render_window
        self.ui_win.connect('key_press_event', self._on_keypress)
        self.view.connect('button_press_event', self._on_button_press)
        self.view.connect('button_release_event', self._on_button_release)
        self.view.connect('motion_notify_event', self._on_mouse_move)
        self.view.add_events(gtk.gdk.BUTTON_PRESS_MASK |
                             gtk.gdk.BUTTON_RELEASE_MASK |
                             gtk.gdk.BUTTON_MOTION_MASK |
			     gtk.gdk.POINTER_MOTION_HINT_MASK)
        self.mappers = []
        self.callbacks = {}
        self.dispatcher = EventDispatcher()
        self.register = self.dispatcher.register
        self.enable = self.dispatcher.enable

    def rotate(self, dx, dy):
        camera = self.ren.GetActiveCamera()
        camera.Azimuth(dx)
        camera.Elevation(dy)
        camera.OrthogonalizeViewUp()
        pos = camera.GetPosition()
        self.redraw()

    def _find_mapper(self, mapper):
        for obj, name in self.mappers:
            if obj is mapper:
                return name
        return None
    
    def _on_button_press(self, unused, event):
        x, y = self.view.get_pointer()
        n = event.button
        self._last_x = x
        self._last_y = y
        h = self.view.window.get_geometry()[3]
        self.dispatcher.handle(self.pick(x, h - y - 1), 'button-press', x, y, n)

    def _on_button_release(self, obj, event):
        x, y = self.view.get_pointer()
        self.dispatcher.handle(None, 'button-release', x, y)

    def _on_keypress(self, unused, event):
        if event.keyval < 256:
            self.dispatcher.handle(None, 'key', chr(event.keyval))

    def _on_mouse_move(self, obj, event):
        x, y = self.view.get_pointer()
        dx, dy = self._last_x - x, self._last_y - y
        camera = self.ren.GetActiveCamera()
        d = self.object
        fov = camera.GetViewAngle() / 180.0 * pi
        width, height = self.view.render_window.GetSize()
        depth = fov * d / height
        up_vec = camera.GetViewUp()
        right_vec = vec_xmul(up_vec, camera.GetViewPlaneNormal())
        v = vec_add(vec_s(right_vec, depth * dx), vec_s(up_vec, -depth * dy))
        rot_v = vec_xmul(v, camera.GetViewPlaneNormal())
        self.dispatcher.handle(None, 'move', dx, dy, v, rot_v)
        self._last_x, self._last_y = x, y

    def add(self, name, obj, color=None, opacity=None):
        mapper = vtkPolyDataMapper()
        mapper.SetInput(obj.GetOutput())
        actor = vtkActor()
        actor.SetMapper(mapper)
        if color is not None:
            actor.GetProperty().SetColor(*color)
        if opacity is not None:
            actor.GetProperty().SetOpacity(opacity)
        self.ren.AddActor(actor)
        self.mappers.append((mapper, name))

    def pick(self, x, y):
        picker = vtkCellPicker()
        if picker.Pick(x, y, 0, self.ren):
            near, far = self.ren.GetActiveCamera().GetClippingRange()
            d = self.ren.GetZ(x, y)
            self.object = d * (far - near) + near
            return self._find_mapper(picker.GetMapper())
        self.object = self.ren.GetActiveCamera().GetDistance()
        return None

    def run(self):
        self.ui_win.show()
        gtk.main()
    def show(self):
        self.ui_win.show()
    def is_alive(self):
        return self.ui_win.get_property("visible")
    def busy(self):
        return gtk.events_pending()
    def handle_event(self):
        return gtk.main_iteration(False)

    def reset_camera(self):
        self.ren.ResetCamera()
        self.redraw()

    def redraw(self):
        self.ren.ResetCameraClippingRange()
        self.view.render()

class MatrixTransform(object):

    def __init__(self):
        self.transform = vtkTransform()
        self.matrix = vtkMatrix4x4()

    def __call__(self, source):
        filter = vtkTransformPolyDataFilter()
        filter.SetInput(source.GetOutput())
        filter.SetTransform(self.transform)
        return filter

    def __setitem__(self, index, val):
        i, j = index
        self.matrix.SetElement(i, j, val)
        self.transform.SetMatrix(self.matrix)

    def __getitem__(self, index):
        i, j = index
        return self.matrix.GetElement(i, j)

arrow = vtkArrowSource()
arrow.SetTipResolution(16)
arrow.SetShaftResolution(16)
cylinder = vtkCylinderSource()
cylinder.SetResolution(16)
sphere = vtkSphereSource()
sphere.SetPhiResolution(16)
sphere.SetThetaResolution(16)
cube = vtkCubeSource()

def filter_from_transform(transform, source):
    filter = vtkTransformPolyDataFilter()
    filter.SetInput(source.GetOutput())
    filter.SetTransform(transform)
    return filter

def rotate_x(amount, source):
    transform = vtkTransform()
    transform.RotateX(amount * 180.0 / pi)
    return filter_from_transform(transform, source)

def rotate_y(amount, source):
    transform = vtkTransform()
    transform.RotateY(amount * 180.0 / pi)
    return filter_from_transform(transform, source)

def rotate_z(amount, source):
    transform = vtkTransform()
    transform.RotateZ(amount * 180.0 / pi)
    return filter_from_transform(transform, source)

def scale(x, y, z, source):
    transform = vtkTransform()
    transform.Scale(x, y, z)
    return filter_from_transform(transform, source)

def translate(x, y, z, source):
    transform = vtkTransform()
    transform.Translate(x, y, z)
    return filter_from_transform(transform, source)

