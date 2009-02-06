from PyKDL import *
from math import pi

segments = [
    Segment(Joint(Joint.RotZ),
            Frame(Rotation.RotX(pi/2), Vector(0, -.045, .225))),
    Segment(Joint(Joint.RotZ),
            Frame(Rotation.RotY(-pi/2), Vector(0, 0, .215))),
    Segment(Joint(Joint.RotZ),
            Frame(Rotation.RotY(pi/2), Vector(.135, 0, 0))),
    Segment(Joint(Joint.None),
            Frame(Rotation.RotY(-pi/2), Vector(0, 0, .175))),
    Segment(Joint(Joint.RotZ),
            Frame(Rotation.RotY(-pi/2), Vector(0, 0, .175))),
    Segment(Joint(Joint.RotZ),
            Frame(Rotation.RotY(pi/2), Vector(.1, 0, 0))),
    Segment(Joint(Joint.TransZ),
            Frame(Rotation.RotY(pi/2), Vector(.1, 0, 0))),
    Segment(Joint(Joint.RotZ),
            Frame(Rotation.RotZ(pi/2), Vector(0, 0, .165)))]
