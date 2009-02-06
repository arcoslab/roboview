from PyKDL import *
from math import pi

segments = [
   Segment(Joint(Joint.None),
     Frame(Rotation.RPY(pi/2, 0, pi/6),Vector(0.07,-0.12124,1.05))),
   Segment(Joint(Joint.RotZ),
     Frame(Vector(0,0,0.225))),
   Segment(Joint(Joint.RotY,-1),
     Frame(Vector(0,-0.26,0))),
   Segment(Joint(Joint.RotX,-1),
     Frame(Vector(0,-0.1,0))),
   Segment(Joint(Joint.RotY,-1),
     Frame(Vector(0,-0.21,0))),
    Segment(Joint(Joint.RotX,-1),
     Frame(Vector(0,0,0))),
    Segment(Joint(Joint.RotY,-1),
     Frame(Vector(0,-0.265,0)))]


