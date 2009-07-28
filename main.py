# roboview.py -- A Robotic Chain Viewer for KDL
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
"""Roboview -- A Robot Viewer for KDL

Usage: roboview [--nav3d-dev <dev>] <file> <prefix>
       roboview [--help]

Where <file> is a python module specifying the robot's structure.

Options:

  --help             Show this help message

Written by Jonathan Kleinehellefort <jk@molb.org>
(c) 2008 Technische Universitaet Muenchen

"""

from math import pi, sqrt
from robot import *
from display import *
import sys
from PyKDL import Frame, Rotation, Vector
import imp
import threading
from ui import RobotWidget

import yarp
import time

prefix=""
# command-line parsing
if len(sys.argv) == 1 or (len(sys.argv) == 2 and sys.argv[1] == '--help'):
    print __doc__
    sys.exit(0)
else:
    if len(sys.argv) == 2:
        robodef_module = sys.argv[1]
    elif len(sys.argv) == 3:
        robodef_module = sys.argv[1]
        prefix= sys.argv[2]
    else:
        print >>sys.stderr, 'Invalid command line arguments!'
        print >>sys.stderr
        print >>sys.stderr, __doc__
        sys.exit(1)

print "Using prefix: %s" %(prefix)
robodef = imp.load_source('robodev', robodef_module)

import gobject
gobject.threads_init()

def vec_smul(u, v):
    ux, uy, uz = u
    vx, vy, vz = v
    return ux*vx + uy*vy + uz*vz

def vec_from_matrix(m):
    return m.p[0], m.p[1], m.p[2]

def vec_abs(v):
    return sqrt(v[0]**2 + v[1]**2 + v[2]**2)

def print_frame(frame):
    for i in range(4):
        for j in range(4):
            print '%.2f\t' % frame[i, j],
        print
    print

class Movable(object):

    def __init__(self):
        self.rot_frame = Frame()
        self.pos = [0.0, 0.0, 0.0]

    def _get_frame(self):
        return Frame(Vector(*self.pos)) * self.rot_frame

    def _set_frame(self, frame):
        self.rot_frame = Frame(frame)
        self.pos = vec_from_matrix(frame)
        x, y, z = self.pos
        self.rot_frame = Frame(Vector(-x, -y, -z)) * self.rot_frame

    frame = property(_get_frame, _set_frame)

    def rot_x(self, v):
        self.rot_frame = Frame(Rotation.RotX(v)) * self.rot_frame

    def rot_y(self, v):
        self.rot_frame = Frame(Rotation.RotY(v)) * self.rot_frame

    def rot_z(self, v):
        self.rot_frame = Frame(Rotation.RotZ(v)) * self.rot_frame

    def rot(self, vec, angle):
        self.rot_frame = Frame(Rotation.Rot(Vector(*vec), angle)) * self.rot_frame

    def pre_translate(self, *v):
        self.pos = vec_add(self.pos, v)

    def translate(self, x, y, z):
        m = Frame(Vector(*self.pos)) * self.rot_frame * Frame(Vector(x, y, z))
        self.pos = vec_from_matrix(m)

class World(object):

    def __init__(self):
        self.robot = Robot(robodef.segments)
        self.ef_ghost = Movable()
        self.grabbed = False
        self.set_ghost_to_ef()

    def set_ghost_to_ef(self):
        self.ef_ghost.frame = self.robot.frame

    def try_set_ef_to_ghost(self):
        if not self.robot.try_move(self.ef_ghost.frame):
            if self.grabbed:
                self.set_ghost_to_ef()

    def grab(self):
        self.grabbed = True

    def ungrab(self):
        self.grabbed = False

    def translate_ghost(self, x, y, z):
        self.ef_ghost.translate(x, y, z)
        if self.grabbed:
            if not self.robot.try_move(self.ef_ghost.frame):
                self.set_ghost_to_ef()
                return False
        return True

    def rotate_ghost(self, x, y, z):
        # yes, i'm aware that rotations are different if carried out in
        # a different order, but i don't care... these are simultaneous
        self.ef_ghost.rot_x(x)
        self.ef_ghost.rot_y(y)
        self.ef_ghost.rot_z(z)
        if self.grabbed:
            if not self.robot.try_move(self.ef_ghost.frame):
                self.set_ghost_to_ef()
                return False
        return True

    def set_joint(self, n, val):
        self.robot[n].value = val
        if self.grabbed:
            self.set_ghost_to_ef()

    def update(self, frame):
        for i, j in [(i, j) for i in range(4) for j in range(4)]:
            self.goal_frame[i, j] = frame[i, j]

class Scene(object):

    def __init__(self, robot): # XXX: try to remove arg
        self.robot = RobotWidget(robot)

    def add_to(self, display):
        self.robot.add_to(display)

class JointController(object):

    def __init__(self, joint, widget):
        self.joint = joint
        self.widget = widget
        def rotate_handler(s):
            self.joint.value += s * 3
            self.handle_change()
        self.widget.rotate_handler = rotate_handler

    def update(self):
        self.widget.update(self.joint.frame, self.joint.value)

class EfController(object):

    def __init__(self, robot, widget):
        self.robot = robot
        self.widget = widget
        self.m = Movable()
        self.m.frame = self.robot.frame
        def translate_handler(dv):
            dv = vec_s(dv, -1)
            self.m.pre_translate(*dv)
            if self.robot.try_move(self.m.frame):
                self.handle_change()
        self.widget.translate_handler = translate_handler
        def rotate_handler(dr):
            self.m.rot(dr, vec_abs(dr) * 3)
            if self.robot.try_move(self.m.frame):
                self.handle_change()
        self.widget.rotate_handler = rotate_handler

    def update(self):
        self.m.frame = self.robot.frame
        self.widget.update(self.robot.frame)

class RobotController(object):

    def __init__(self, robot, robot_widget):
        self.robot = robot
        self.robot_widget = robot_widget
        self.joint_controllers = set()
        for joint, joint_widget in zip(robot, self.robot_widget.joint_widgets):
            joint_controller = JointController(joint, joint_widget)
            def handle_change():
                self.handle_change()
            joint_controller.handle_change = handle_change
            self.joint_controllers.add(joint_controller)
        self.ef_controller = EfController(robot, robot_widget.ef_widget)
        def handle_change():
            self.handle_change()
        self.ef_controller.handle_change = handle_change

    def update(self):
        for joint_controller in self.joint_controllers:
            joint_controller.update()
        #self.robot_widget.update([j.frame for j in self.robot] + [self.robot.frame])
        self.ef_controller.update()

class EfGhostController(object):

    def __init__(self, ghost, view):
        self.ghost = ghost
        self.view = view

    def update(self):
        self.view.update(self.ghost.frame)

class Controller(object):

    def __init__(self, world, scene):
        self.world = world
        self.scene = scene
        self.robot_controller = RobotController(world.robot, scene.robot)
        def handle_change():
            self.robot_controller.update()
            self.update()
        self.robot_controller.handle_change = handle_change
        self.need_update = False

    def update(self, hard=False):
        def _update():
            if self.need_update:
                self.robot_controller.update()
                display.redraw()
                self.need_update = False
        self.need_update = True
        if hard:
            _update()
        else:
            gobject.idle_add(_update)

display = Display()

# the world model
world = World()

# the scene graph
scene = Scene(world.robot)

scene.add_to(display)

controller = Controller(world, scene)
controller.update(hard=True)

# event handlers

def grab_handler(i, dx, dy):
    world.robot[i].value += dx / 100.0
    controller.update()

scene.robot.grab_handler = grab_handler

def handle_key(c):
    if c == 'r':
        display.reset_camera()
    elif c == 'q':
        sys.exit(0)
    elif c == 'g':
        world.grab()
        controller.update()
    elif c == 'u':
        world.ungrab()
    elif c == 's':
        world.set_ghost_to_ef()
        controller.update()

def enable_rotation(x, y, n):
    if n == 1:
        display.enable('rotating')
    elif n == 2:
        display.enable('paning')

def rotate(dx, dy, dv, dr):
    display.rotate(dx, dy)

def vec_add(u, v):
    return [ue + ve for ue, ve in zip(u, v)]

def vec_s(v, s):
    return [ve * s for ve in v]

def pan(dx, dy, dv, dr):
    camera = display.ren.GetActiveCamera()
    pos = camera.GetPosition()
    foc = camera.GetFocalPoint()
    camera.SetPosition(vec_add(pos, dv))
    camera.SetFocalPoint(vec_add(foc, dv))
    display.redraw()

def reset_state(*args):
    display.enable(None)

display.register(None, None, 'button-press', enable_rotation)
display.register('rotating', None, 'button-release', reset_state)
display.register('rotating', None, 'move', rotate)
display.register('paning', None, 'button-release', reset_state)
display.register('paning', None, 'move', pan)
display.register(None, None, 'key', handle_key)

def set_joint(*args):
    world.set_joint(*args)
    controller.update()

def update_joints_main():
    import time
    while True:
        time.sleep(5)
        gobject.idle_add(set_joint, 2, pi/2.0,
                         priority=gobject.PRIORITY_HIGH_IDLE)

#threading.Thread(target=update_joints_main).start()

#display.run()

rate = 0.02 # [s]
display_multiplier = 4

qin=yarp.BufferedPortBottle()
qin.open(prefix+"/roboview/qin")
qvin=yarp.BufferedPortBottle()
qvin.open(prefix+"/roboview/qvin")
qout=yarp.BufferedPortBottle()
qout.open(prefix+"/roboview/qout")

display.show()

finalTime = time.time()
display_counter=0

num_joints = world.robot.jnt_pos.rows()
vels = [0]*num_joints

while display.is_alive():
  initTime = time.time()
  while display.busy() and (time.time() - initTime) < rate*0.8:
    display.handle_event()

  # write current position
  bot=qout.prepare()
  bot.clear()
  for i in range(num_joints):
    bot.addDouble(world.robot.jnt_pos[i])
  qout.write()

  # read commanded position
  bottlein = qin.read(False)
  if bottlein and bottlein.size() == num_joints:
    for i in range(num_joints):
      world.robot.jnt_pos[i] = bottlein.get(i).asDouble()

  # read commanded velocities
  bottlein = qvin.read(False)
  if bottlein and bottlein.size() == num_joints:
    for i in range(num_joints):
      vels[i] = bottlein.get(i).asDouble()

  # handle limits
  if robodef.limits_min and robodef.limits_max:
    for i in range (num_joints):
     world.robot.jnt_pos[i] = min(robodef.limits_max[i],
                               max(robodef.limits_min[i],
                                world.robot.jnt_pos[i]))

  # refresh display
  if display_counter == display_multiplier:
    display.redraw()
    controller.update()
    display_counter=0
  else:
    display_counter=display_counter+1

  # apply velocities
  factor = time.time()-finalTime
  for i in range (num_joints):
    world.robot.jnt_pos[i] = world.robot.jnt_pos[i] + vels[i]*factor
  
  #print "factor: "+str(factor)+" "+reduce(str.__add__,[str(v)+" " for v in vels])

  # handle sleeping
  finalTime = time.time()
  sleepTime = rate - (finalTime - initTime)
  if sleepTime>0:
    time.sleep(sleepTime)

  initTime = time.time()

