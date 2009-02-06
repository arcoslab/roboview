from PyKDL import *
from math import pi

segments = [
    Segment(Joint(Joint.RotY),
            Frame(Rotation.Identity(), Vector(0.10, 0.23, 0.0))),
    Segment(Joint(Joint.RotX),
            Frame(Rotation.Identity(), Vector(0, 0.1, 0.0))),
    Segment(Joint(Joint.RotY),
            Frame(Rotation.Identity(), Vector(0, 0.25, 0))),
    Segment(Joint(Joint.RotX),
            Frame(Rotation.Identity(), Vector(0, 0.43, 0.0)))]
