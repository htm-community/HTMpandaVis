# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

from direct.showbase.ShowBase import ShowBase
from panda3d.core import LColor
 
class MyApp(ShowBase):
 
    def __init__(self):
        ShowBase.__init__(self)
                
         # Load the environment model.
        self.teapot = self.loader.loadModel("models/teapot")
        self.cube = self.loader.loadModel("/media/Data/Data/Panda3d/cube.egg")
        # Reparent the model to render.
        self.teapot.reparentTo(self.render)
        self.cube.reparentTo(self.render)
        # Apply scale and position transforms on the model.
        self.cube.setScale(10, 10, 10)
        self.cube.setPos(-8, 42, 0)
        
        self.cube.setColor(1.0,0,0,1.0)
        self.cube.setRenderModeThickness(5)
        
        self.cube.setRenderModeFilledWireframe(LColor(0,0,0,1.0))
        
        self.teapot.setScale(0.25, 0.25, 0.25)
        self.teapot.setPos(-8, 42, 0)
app = MyApp()
app.run()

