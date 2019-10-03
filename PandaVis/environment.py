#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from panda3d.core import DirectionalLight, AmbientLight, AntialiasAttrib
from panda3d.core import LColor, CollisionBox, CollisionNode
from panda3d.core import (
    GeomVertexFormat,
    GeomVertexData,
    GeomVertexWriter,
    Geom,
    GeomLines,
    GeomNode,
    PerspectiveLens,
)

verbosityLow = 0
verbosityMedium = 1
verbosityHigh = 2
FILE_VERBOSITY = (
    verbosityHigh
)  # change this to change printing verbosity of this file


def printLog(txt, verbosity=verbosityLow):
    if FILE_VERBOSITY >= verbosity:
        print(txt)
        
class cEnvironment:
    
    def __init__(self,base):
        self.base = base
        self.render = base.render
        
    def SetupCamera(self):
        width = self.base.win.getProperties().getXSize()
        height = self.base.win.getProperties().getYSize()
        lens = PerspectiveLens()
        lens.setFov(60)

        lens.setAspectRatio(width / height)
        # lens.setFilmSize(width,height)
        # lens.setFocalLength(self.FOCAL_LENGTH)
        lens.setFar(500.0)
        self.base.cam.node().setLens(lens)

        self.base.camera.setPos(100, -80, 0)
        self.base.camHeading = 40.0
        self.base.camPitch = -8.0
        
    def SetupLights(self):
        # Create Ambient Light
        ambientLight = AmbientLight('ambientLight')
        ambientLight.setColor((0.2, 0.2, 0.2, 1))
        self.ambLight  = self.render.attachNewNode(ambientLight)
        self.render.setLight(self.ambLight)
        
        # Directional light 01
        directionalLight1 = DirectionalLight('directionalLight')
        directionalLight1.setColor((1, 1, 1, 1))
        self.dirLight1 = self.render.attachNewNode(directionalLight1)
        
        # This light is facing backwards, towards the camera.
        self.dirLight1.setHpr(40, -40, 0)
        self.render.setLight(self.dirLight1)
        
        directionalLight2 = DirectionalLight('directionalLight')
        directionalLight2.setColor((0.9, 0.9, 0.9, 1))
        self.dirLight2 = self.render.attachNewNode(directionalLight2)
        
        # This light is facing backwards, towards the camera.
        self.dirLight2.setHpr(180+40, 30, 0)
        self.render.setLight(self.dirLight2)
        
        self.render.setAntialias(AntialiasAttrib.MLine)
        
    def CreateBasement(
        self
    ):  # it will create basement object, just for case that nothing is drawn to be not lost
    
        # Load the environment model.
        self.cube = self.base.loader.loadModel("models/cube")  # /media/Data/Data/Panda3d/
    
        # Reparent the model to render.
        self.cube.reparentTo(self.render)
        # Apply scale and position transforms on the model.
    
        self.cube.setScale(10, 10, 10)
        self.cube.setPos(-8, -40, 0)
    
        self.cube.setColor(1.0, 0, 0, 1.0)
        self.cube.setRenderModeThickness(5)
    
        self.cube.setRenderModeFilledWireframe(LColor(0, 0, 0, 1.0))
        # COLLISION
        collBox = CollisionBox(self.cube.getPos(), 10.0, 10.0, 10.0)
        cnodePath = self.cube.attachNewNode(CollisionNode("cnode"))
        cnodePath.node().addSolid(collBox)
    
        self.cube.setTag("clickable", "1")
    
    def CreateTestScene(self):
    
        form = GeomVertexFormat.getV3()
        vdata = GeomVertexData("myLine", form, Geom.UHStatic)
        vdata.setNumRows(1)
        vertex = GeomVertexWriter(vdata, "vertex")
    
        vertex.addData3f(0, 0, 0)
        vertex.addData3f(60, 0, 50)
    
        prim = GeomLines(Geom.UHStatic)
        prim.addVertices(0, 1)
    
        geom = Geom(vdata)
        geom.addPrimitive(prim)
    
        node = GeomNode("gnode")
        node.addGeom(geom)
    
        nodePath = self.render.attachNewNode(node)
    
        # self.HTMObjects.CreateInput("IN 1",count=500,rows=int(math.sqrt(500)))
        # self.HTMObjects.CreateLayer("SP/TM 1",nOfColumnsPerLayer=200,nOfCellsPerColumn=10)
