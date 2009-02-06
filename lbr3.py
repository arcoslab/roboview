from PyKDL import *
from math import pi

segments = [
   Segment(Joint(Joint.None),
     Frame(Rotation(),Vector(0,0,0.110))),
   Segment(Joint(Joint.RotZ),
     Frame(Rotation.RotX(-pi/2),Vector(0,0,0.200))),
   Segment(Joint(Joint.RotZ),
     Frame(Rotation.RotX(pi/2),Vector(0,-0.200,0))),
   Segment(Joint(Joint.RotZ),
     Frame(Rotation.RotX(-pi/2),Vector(0,0.0,0.200))),
   Segment(Joint(Joint.RotZ,-1),
     Frame(Rotation.RotX(pi/2),Vector(0,-0.200,0))),
    Segment(Joint(Joint.RotZ),
     Frame(Rotation.RotX(-pi/2),Vector(0,0,0.190))),
    Segment(Joint(Joint.RotZ),
     Frame(Rotation.RotX(pi/2),Vector(0,-0.078,0))),
    Segment(Joint(Joint.RotZ),
     Frame(Vector(0,0,0.100))),
     ]


