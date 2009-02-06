# gtkvtk.py -- A Gtk Widget for Rendering VTK Scenes
# -*- coding: utf-8 -*-
#
# Written by Jonathan Kleinehellefort <jk@molb.org>, based on
# GtkVTKRenderWindow.py from VTK <http://www.vtk.org/> by Prabhu
# Ramachandran, in turn based on vtkTkRenderWidget.py by David Gobbi.
#
# Copyright 2008 Lehrstuhl Bildverstehen und wissensbasierte Systeme,
#                Technische Universität München
# Copyright 1993-2008 Ken Martin
# Copyright 1993-2008 Will Schroeder
# Copyright 1993-2008 Bill Lorensen
# Copyright 2001-2002 Prabhu Ramachandran
# Copyright 1999-2000 David Gobbi
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#
#  * Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
#
#  * Neither name of Ken Martin, Will Schroeder, or Bill Lorensen nor
#    the names of any contributors may be used to endorse or promote
#    products derived from this software without specific prior
#    written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# ``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# AUTHORS OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import gtk
import gtk.gtkgl
import vtk
import math


class VtkRenderArea(gtk.gtkgl.DrawingArea):

    """ A base class that enables one to embed a vtkRenderWindow into
    a pyGTK widget.  This class embeds the RenderWindow correctly.
    Provided are some empty methods that can be overloaded to provide
    a user defined interaction behaviour.  The event handling
    functions have names that are somewhat similar to the ones in the
    vtkInteractorStyle class included with VTK. """

    def __init__(self, *args, **kwargs):

        #display_mode = (gtk.gdkgl.MODE_RGBA | gtk.gdkgl.MODE_DOUBLE)
        #glconfig = gtk.gdkgl.Config(mode=display_mode)
        #gtk.gtkgl.DrawingArea.__init__(self, glconfig, *args, **kwargs)
        gtk.gtkgl.DrawingArea.__init__(self, *args, **kwargs)

        self.render_window = vtk.vtkRenderWindow()

        # private attributes
        self.__created = False
        
        def on_realize(*unused):
            if not self.__created:
                # you can't get the xid without the window being realized.
                self.realize()
                self.render_window.SetWindowInfo('%d' % self.window.xid)
                self.__created = True
                return True
        self.connect('realize', on_realize)

        def on_configure(unused, event):
            width, height = self.render_window.GetSize()
            if event.width != width or event.height != height:
                self.render_window.SetSize(event.width, event.height)
                return True
        self.connect('configure_event', on_configure)

        def on_expose(*unused):
            self.render()
            return True
        self.connect('expose_event', on_expose)

        def on_destroy(*unused):
            self.hide()
            del self.render_window
            self.destroy()
            return True
        self.connect('delete_event', on_destroy)

        self.add_events(gtk.gdk.EXPOSURE_MASK)

    def render(self):
        if self.__created:
            self.render_window.Render()


class VtkSceneViewer(VtkRenderArea):

    """ An example of a fully functional GtkVTKRenderWindow that is
    based on the vtkRenderWidget.py provided with the VTK sources."""

    def __init__(self, *args, **kwargs):
        VtkRenderArea.__init__(self, *args, **kwargs)
        
        self._CurrentRenderer = None
        self._CurrentCamera = None
        self._CurrentZoom = 1.0
        self._CurrentLight = None

        self._ViewportCenterX = 0
        self._ViewportCenterY = 0
        
        self._Picker = vtk.vtkCellPicker()
        self._PickedAssembly = None
        self._PickedProperty = vtk.vtkProperty()
        self._PickedProperty.SetColor(1, 0, 0)
        self._PrePickedProperty = None
        
        self._OldFocus = None

        # need this to be able to handle key_press events.
        self.set_flags(gtk.CAN_FOCUS)

        # these record the previous mouse position
        self._LastX = 0
        self._LastY = 0

        self.connect('button_press_event', self.OnButtonDown)
        self.connect('button_release_event', self.OnButtonUp)
        self.connect('motion_notify_event', self.OnMouseMove)
        self.connect('key_press_event', self.OnKeyPress)
        self.add_events(gtk.gdk.BUTTON_PRESS_MASK |
                        gtk.gdk.BUTTON_RELEASE_MASK |
                        gtk.gdk.KEY_PRESS_MASK |
                        gtk.gdk.POINTER_MOTION_MASK |
                        gtk.gdk.POINTER_MOTION_HINT_MASK)

    def OnButtonDown(self, wid, event):
        self.grab_focus()
        return self.StartMotion(wid, event)
    
    def OnButtonUp(self, wid, event):
        return self.EndMotion(wid, event)

    def OnMouseMove(self, wid, event=None):
        if (event.state & gtk.gdk.BUTTON1_MASK) == gtk.gdk.BUTTON1_MASK:
            if (event.state & gtk.gdk.SHIFT_MASK) == gtk.gdk.SHIFT_MASK:
                m = self.get_pointer()
                self.Pan(m[0], m[1])
                return True
            else:
                m = self.get_pointer()
                self.Rotate(m[0], m[1])
                return True
        elif (event.state & gtk.gdk.BUTTON2_MASK) == gtk.gdk.BUTTON2_MASK:
            m = self.get_pointer()
            self.Pan(m[0], m[1])
            return True
        elif (event.state & gtk.gdk.BUTTON3_MASK) == gtk.gdk.BUTTON3_MASK:
            m = self.get_pointer()
            self.Zoom(m[0], m[1])
            return True
        else:
            return False

    def OnKeyPress(self, wid, event=None):
        if event.keyval == ord('r'):
            self.Reset()
            return True
        elif event.keyval == ord('w'):
            self.Wireframe()
            return True
        elif event.keyval == ord('s'):
            self.Surface()
            return True
        elif event.keyval == ord('p'):
            m = self.get_pointer()
            self.pick_actor(m[0], m[1])
            return True
        else:
            return False

    def render(self):
        if (self._CurrentLight):
            light = self._CurrentLight
            light.SetPosition(self._CurrentCamera.GetPosition())
            light.SetFocalPoint(self._CurrentCamera.GetFocalPoint())
        VtkRenderArea.render(self)

    def UpdateRenderer(self, x, y):
        """
        UpdateRenderer will identify the renderer under the mouse and set
        up _CurrentRenderer, _CurrentCamera, and _CurrentLight.
        """
        windowX, windowY =  self.window.get_geometry()[2:4]

        renderers = self.render_window.GetRenderers()
        numRenderers = renderers.GetNumberOfItems()

        self._CurrentRenderer = None
        renderers.InitTraversal()
        for i in range(0,numRenderers):
            renderer = renderers.GetNextItem()
            vx,vy = (0,0)
            if (windowX > 1):
                vx = float(x)/(windowX-1)
            if (windowY > 1):
                vy = (windowY-float(y)-1)/(windowY-1)
            (vpxmin,vpymin,vpxmax,vpymax) = renderer.GetViewport()
            
            if (vx >= vpxmin and vx <= vpxmax and
                vy >= vpymin and vy <= vpymax):
                self._CurrentRenderer = renderer
                self._ViewportCenterX = float(windowX)*(vpxmax-vpxmin)/2.0\
                                        +vpxmin
                self._ViewportCenterY = float(windowY)*(vpymax-vpymin)/2.0\
                                        +vpymin
                self._CurrentCamera = self._CurrentRenderer.GetActiveCamera()
                lights = self._CurrentRenderer.GetLights()
                lights.InitTraversal()
                self._CurrentLight = lights.GetNextItem()
                break

        self._LastX = x
        self._LastY = y

    def GetCurrentRenderer(self):
        return self._CurrentRenderer
                
    def StartMotion(self, wid, event=None):
        x = event.x
        y = event.y
        self.UpdateRenderer(x, y)
        return True

    def EndMotion(self, wid, event=None):
        if self._CurrentRenderer:
            self.render()
        return True

    def Rotate(self,x,y):
        if self._CurrentRenderer:
            
            self._CurrentCamera.Azimuth(self._LastX - x)
            self._CurrentCamera.Elevation(y - self._LastY)
            self._CurrentCamera.OrthogonalizeViewUp()
            
            self._LastX = x
            self._LastY = y
            
            self._CurrentRenderer.ResetCameraClippingRange()
            self.render()

    def Pan(self,x,y):
        if self._CurrentRenderer:
            
            renderer = self._CurrentRenderer
            camera = self._CurrentCamera
            (pPoint0,pPoint1,pPoint2) = camera.GetPosition()
            (fPoint0,fPoint1,fPoint2) = camera.GetFocalPoint()

            if (camera.GetParallelProjection()):
                renderer.SetWorldPoint(fPoint0,fPoint1,fPoint2,1.0)
                renderer.WorldToDisplay()
                fx,fy,fz = renderer.GetDisplayPoint()
                renderer.SetDisplayPoint(fx-x+self._LastX,
                                         fy+y-self._LastY,
                                         fz)
                renderer.DisplayToWorld()
                fx,fy,fz,fw = renderer.GetWorldPoint()
                camera.SetFocalPoint(fx,fy,fz)

                renderer.SetWorldPoint(pPoint0,pPoint1,pPoint2,1.0)
                renderer.WorldToDisplay()
                fx,fy,fz = renderer.GetDisplayPoint()
                renderer.SetDisplayPoint(fx-x+self._LastX,
                                         fy+y-self._LastY,
                                         fz)
                renderer.DisplayToWorld()
                fx,fy,fz,fw = renderer.GetWorldPoint()
                camera.SetPosition(fx,fy,fz)
                
            else:
                (fPoint0,fPoint1,fPoint2) = camera.GetFocalPoint()
                # Specify a point location in world coordinates
                renderer.SetWorldPoint(fPoint0,fPoint1,fPoint2,1.0)
                renderer.WorldToDisplay()
                # Convert world point coordinates to display coordinates
                dPoint = renderer.GetDisplayPoint()
                focalDepth = dPoint[2]
                
                aPoint0 = self._ViewportCenterX + (x - self._LastX)
                aPoint1 = self._ViewportCenterY - (y - self._LastY)
                
                renderer.SetDisplayPoint(aPoint0,aPoint1,focalDepth)
                renderer.DisplayToWorld()
                
                (rPoint0,rPoint1,rPoint2,rPoint3) = renderer.GetWorldPoint()
                if (rPoint3 != 0.0):
                    rPoint0 = rPoint0/rPoint3
                    rPoint1 = rPoint1/rPoint3
                    rPoint2 = rPoint2/rPoint3

                camera.SetFocalPoint((fPoint0 - rPoint0) + fPoint0, 
                                     (fPoint1 - rPoint1) + fPoint1,
                                     (fPoint2 - rPoint2) + fPoint2) 
                
                camera.SetPosition((fPoint0 - rPoint0) + pPoint0, 
                                   (fPoint1 - rPoint1) + pPoint1,
                                   (fPoint2 - rPoint2) + pPoint2)

            self._LastX = x
            self._LastY = y

            self.render()

    def Zoom(self,x,y):
        if self._CurrentRenderer:

            renderer = self._CurrentRenderer
            camera = self._CurrentCamera

            zoomFactor = math.pow(1.02,(0.5*(self._LastY - y)))
            self._CurrentZoom = self._CurrentZoom * zoomFactor

            if camera.GetParallelProjection():
                parallelScale = camera.GetParallelScale()/zoomFactor
                camera.SetParallelScale(parallelScale)
            else:
                camera.Dolly(zoomFactor)
                renderer.ResetCameraClippingRange()

            self._LastX = x
            self._LastY = y

            self.render()

    def Reset(self):
        if self._CurrentRenderer:
            self._CurrentRenderer.ResetCamera()
            
        self.render()

    def Wireframe(self):
        actors = self._CurrentRenderer.GetActors()
        numActors = actors.GetNumberOfItems()
        actors.InitTraversal()
        for i in range(0,numActors):
            actor = actors.GetNextItem()
            actor.GetProperty().SetRepresentationToWireframe()

        self.render()
        
    def Surface(self):
        actors = self._CurrentRenderer.GetActors()
        numActors = actors.GetNumberOfItems()
        actors.InitTraversal()
        for i in range(0,numActors):
            actor = actors.GetNextItem()
            actor.GetProperty().SetRepresentationToSurface()

        self.render()

    def pick_actor(self, x, y):
        if self._CurrentRenderer:

            renderer = self._CurrentRenderer
            picker = self._Picker
            
            windowY = self.window.get_geometry()[3]
            picker.Pick(x,(windowY - y - 1),0.0,renderer)
            assembly = picker.GetAssembly()

            if (self._PickedAssembly != None and
                self._PrePickedProperty != None):
                self._PickedAssembly.SetProperty(self._PrePickedProperty)
                # release hold of the property
                self._PrePickedProperty.UnRegister(self._PrePickedProperty)
                self._PrePickedProperty = None

            if (assembly != None):
                self._PickedAssembly = assembly
                self._PrePickedProperty = self._PickedAssembly.GetProperty()
                # hold onto the property
                self._PrePickedProperty.Register(self._PrePickedProperty)
                self._PickedAssembly.SetProperty(self._PickedProperty)

            self.render()


if __name__ == '__main__':

    # The main window
    window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    window.set_title('Demo of GTK/VTK integration')
    window.connect('destroy', gtk.main_quit)
    #window.connect('delete_event', gtk.main_quit)

    # A VBox into which widgets are packed.
    vbox = gtk.VBox()
    window.add(vbox)
    vbox.show()

    # The VtkRenderWindow
    gvtk = VtkSceneViewer()
    #gvtk.SetDesiredUpdateRate(1000)
    gvtk.set_size_request(400, 400)
    vbox.pack_start(gvtk)
    gvtk.show()

    # The VTK stuff.
    cone = vtk.vtkConeSource()
    cone.SetResolution(80)
    coneMapper = vtk.vtkPolyDataMapper()
    coneMapper.SetInput(cone.GetOutput())
    #coneActor = vtk.vtkLODActor()
    coneActor = vtk.vtkActor()
    coneActor.SetMapper(coneMapper)    
    coneActor.GetProperty().SetColor(0.5, 0.5, 1.0)
    ren = vtk.vtkRenderer()
    gvtk.render_window.AddRenderer(ren)
    ren.AddActor(coneActor)

    # A simple quit button
    quit = gtk.Button("Quit!")
    quit.connect("clicked", gtk.main_quit)
    vbox.pack_start(quit, expand=False)
    quit.show()

    # show the main window and start event processing.
    window.show()
    gtk.main()
