from PyKDL import *
from math import pi

#segments = [
#   Segment(Joint(Joint.None),
#     Frame(Rotation(),Vector(0,0,0.110))),
#   Segment(Joint(Joint.RotZ),
#     Frame(Rotation.RotX(-pi/2),Vector(0,0,0.200))),
#   Segment(Joint(Joint.RotZ),
#     Frame(Rotation.RotX(pi/2),Vector(0,-0.200,0))),
#   Segment(Joint(Joint.RotZ),
#     Frame(Rotation.RotX(-pi/2),Vector(0,0.0,0.200))),
#   Segment(Joint(Joint.RotZ,-1),
#     Frame(Rotation.RotX(pi/2),Vector(0,-0.200,0))),
#    Segment(Joint(Joint.RotZ),
#     Frame(Rotation.RotX(-pi/2),Vector(0,0,0.190))),
#    Segment(Joint(Joint.RotZ),
#     Frame(Rotation.RotX(pi/2),Vector(0,-0.078,0))),
#    Segment(Joint(Joint.RotZ),
#     Frame(Vector(0,0,0.100))),
#     ]

segments = [
  Segment(Joint(Joint.None),
    Frame(Rotation.Identity(), Vector(0.0, 0.0, 0.11))),
  Segment(Joint(Joint.RotZ),
    Frame(Rotation.RotX(-pi/2), Vector(0.0, 0.0, 0.20))),
  Segment(Joint(Joint.RotZ),
    Frame(Rotation.RotX(pi/2), Vector(0.0, -0.20, 0.0))),
  Segment(Joint(Joint.RotZ),
    Frame(Rotation.RotX(pi/2), Vector(0, 0, .20))),
  Segment(Joint(Joint.RotZ),
    Frame(Rotation.RotX(-pi/2), Vector(0, 0.2, 0))),
  Segment(Joint(Joint.RotZ),
    Frame(Rotation.RotX(-pi/2), Vector(0, 0, 0.19))),
  Segment(Joint(Joint.RotZ),
    Frame(Rotation.RotX(pi/2), Vector(0, -0.078, 0.0))),
  Segment(Joint(Joint.RotZ),
    Frame(Rotation.RotZ(pi/4)*Rotation.RotY(pi/2), Vector(0.075, 0.075, -0.094))), #To wrist
  Segment(Joint(Joint.None),
    Frame(Rotation.Identity(), Vector(0.07, 0.025, 0.28)))  #To fingertips
    ]


limits_min = [-169.9, -119.9, -169.9, -119.9, -169.9, -130.1, -170.1]
limits_max = [ 169.9,  119.9,  169.9,  119.9,  169.9,  130.1,  170.1]

limits_min = [v*pi/180.0 for v in limits_min]
limits_max = [v*pi/180.0 for v in limits_max]

