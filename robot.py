# robot.py -- Model a Robot using KDL
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

from PyKDL import *
from math import pi
import yarp

_type_to_str = {
    Joint.RotX: 'rot_x',
    Joint.RotY: 'rot_y',
    Joint.RotZ: 'rot_z',
    Joint.TransX: 'trans_x',
    Joint.TransY: 'trans_y',
    Joint.TransZ: 'trans_z',
    Joint.None: 'none'}

class RJoint(object):
        
    def __init__(self, robot, i, n):
        self.robot = robot
        self.i = i
        self.n = n

    def _get_frame(self):
        frame = Frame()
        #self.robot.fk_solver.JntToCart(self.robot.jnt_pos, frame)
        self.robot.fk_solver.JntToCart(self.robot.jnt_pos, frame, self.i)
        return frame

    frame = property(_get_frame)

    def _get_static_transform(self):
        return self.robot.segments[self.i].pose(0)

    static_transform = property(_get_static_transform)

    def _get_type(self):
        return _type_to_str[self.robot.segments[self.i].getJoint().getType()]

    type = property(_get_type)

    def _get_value(self):
        return self.robot.jnt_pos[self.n]

    def _set_value(self, value):
        self.robot.jnt_pos[self.n] = value

    value = property(_get_value, _set_value)

class Robot(object):

    def __init__(self, segments):
        self.chain = Chain()
        self.segments = segments
        for segment in segments:
            self.chain.addSegment(segment)
        self.jnt_pos = JntArray(self.chain.getNrOfJoints())
        self.fk_solver = ChainFkSolverPos_recursive(self.chain)
        self.ikv_solver = ChainIkSolverVel_pinv(self.chain)
        self.ik_solver = ChainIkSolverPos_NR(self.chain,
                                             self.fk_solver,
                                             self.ikv_solver)

        self.joints = []
        n = 0
        for i, seg in enumerate(self.segments):
            self.joints.append(RJoint(self, i, n))
            if seg.getJoint().getType() != Joint.None:
                n += 1
        self.qout=yarp.BufferedPortBottle()
        self.qout.open("/roboview/qout")


    def __iter__(self):
        return iter(self.joints)

    def __getitem__(self, i):
        return self.joints[i]

    def _get_frame(self):
        frame = Frame()
        self.fk_solver.JntToCart(self.jnt_pos, frame)
        return frame

    frame = property(_get_frame)

    def try_move(self, frame):
        #kdl_frame = Frame()
        #for i, j in [(i, j) for i in range(4) for j in range(4)]:
        #    kdl_frame[i, j] = frame[i, j]
        jnt_pos = JntArray(self.jnt_pos)

        if self.ik_solver.CartToJnt(jnt_pos, frame, jnt_pos) == 0:
            self.jnt_pos = jnt_pos
            bot=self.qout.prepare()
            bot.clear()

            for i in range(jnt_pos.rows()):
                bot.addDouble(jnt_pos[i])

            self.qout.write()

            return True
        else:
            return False

__all__ = ['Robot']
