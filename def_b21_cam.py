from PyKDL import *
from math import pi

#DH:  a  alpha  d  tetha
segments = [
        Segment(Joint(Joint.None),
                Frame(Rotation.Identity(), Vector(0.07,0,1.29))),
        Segment(Joint(Joint.None),
                Frame(Rotation.Identity(), Vector(0.0,0.0,0.053))),
        Segment(Joint(Joint.RotZ),
                Frame(Rotation.Identity(), Vector(0.0,0.0,0.046))),
        Segment(Joint(Joint.RotY),
                Frame(Rotation.RotY(pi/2.0)*Rotation.RotZ(-pi/2.0), Vector(0.0, -0.084, 0.06))), #-0.084 for the right cam, +0.084 for the left one
        ]
        
#        Segment(Joint(Joint.TransX),
#                Frame(Rotation.Identity(), Vector(0,0,0))),
#        Segment(Joint(Joint.TransY),
#                Frame(Rotation.Identity(), Vector(0,0,0))),
#        Segment(Joint(Joint.TransZ),
#                Frame(Rotation.Identity(), Vector(0,0,0)))
#        ]

