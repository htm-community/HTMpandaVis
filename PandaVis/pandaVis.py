#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from direct.showbase.ShowBase import ShowBase
from panda3d.core import LColor,CollisionBox
from panda3d.core import GeomVertexFormat, GeomVertexData, GeomVertexWriter,Geom,GeomLines,GeomNode,PerspectiveLens

from pandaComm.client import SocketClient
import math

from panda3d.core import CollisionTraverser,CollisionNode
from panda3d.core import CollisionHandlerQueue,CollisionRay
    
from objects.htmObject import cHTM 
from gui import cGUI


verbosityLow = 0
verbosityMedium = 1
verbosityHigh = 2
FILE_VERBOSITY = verbosityMedium # change this to change printing verbosity of this file

def printLog(txt, verbosity=verbosityLow):
  if FILE_VERBOSITY>=verbosity:
    print(txt)
        
    
class cApp(ShowBase):
 
    FOCAL_LENGTH = 500
    
    focusCursor = None
    
    def __init__(self):
        ShowBase.__init__(self)
        
        self.speed = 20
        
        # Mouse and camera movement init
        self.mouseX_last=0
        self.mouseY_last=0
        self.rotateCamera=False
        self.move_z=50
        
        self.CreateBasement()#to not be lost if there is nothing around
        
        self.SetupCameraAndKeys()
        self.taskMgr.add(self.update, 'main loop')
        self.accept(self.win.getWindowEvent(),self.onWindowEvent)
        
        
        width = self.win.getProperties().getXSize()
        height = self.win.getProperties().getYSize()
        
        self.gui = cGUI(width,height,self.loader,fSpeedChange=self.onSpeedChange,defaultSpeed=self.speed)
        
        #self.gui.cBox.command = self.setWireFrame
                
        #self.CreateTestScene()
        
        self.SetupOnClick()
        
        self.client = SocketClient()
        self.client.setGui(self.gui)
        
    
        self.HTMObjects = {}
        
        self.focusedCell = None
        self.focusedPath = None
        self.speedBoost = False
        
        #self.pixel2d.reparentTo(self.render2d)
        
        
    def onSpeedChange(self,value):
        try:
            self.speed = int(value)
        except:
            return
      
    def SetupCameraAndKeys(self):
        # Setup controls
        self.keys = {}
        for key in ['arrow_left', 'arrow_right', 'arrow_up', 'arrow_down',
                    'a', 'd', 'w', 's','shift','control','space']:
            self.keys[key] = 0
            self.accept(key, self.onKey, [key, 1])
            self.accept('shift-%s' % key, self.onKey, [key, 1])
            self.accept('%s-up' % key, self.onKey, [key, 0])
        
        self.accept('escape', self.onEscape, [])
        self.disableMouse()

        # Setup camera
        width = self.win.getProperties().getXSize()
        height = self.win.getProperties().getYSize()
        lens = PerspectiveLens()
        lens.setFov(60)

        lens.setAspectRatio(width/height)
        #lens.setFilmSize(width,height)
        #lens.setFocalLength(self.FOCAL_LENGTH)
        lens.setFar(500.0)
        self.cam.node().setLens(lens)
        
        self.camera.setPos(40, -80, 0)
        self.heading = 0.0
        self.pitch = -30.0
        
        
        self.accept('mouse1',self.onMouseEvent,["left",True])
        self.accept('mouse1-up',self.onMouseEvent,["left",False])
        self.accept('mouse3',self.onMouseEvent,["right",True])
        self.accept('mouse3-up',self.onMouseEvent,["right",False])
      
      
    def SetupOnClick(self):
      
      pickerNode = CollisionNode('mouseRay')
      pickerNP = self.camera.attachNewNode(pickerNode)
      pickerNode.setFromCollideMask(CollisionNode.getDefaultCollideMask())#GeomNode.getDefaultCollideMask())
      self.pickerRay = CollisionRay()
      pickerNode.addSolid(self.pickerRay)
      
      self.myTraverser = CollisionTraverser('mouseCollisionTraverser')
      
      #self.myTraverser.showCollisions(self.render) #uncomment to see collision point
      
      self.myHandler = CollisionHandlerQueue()
      
      self.myTraverser.addCollider(pickerNP,self.myHandler)
        
    
    def CloseApp(self):
      
      printLog("CLOSE app event")
      __import__('sys').exit(0)
      self.client.terminateClientThread=True
      
    def onWindowEvent(self,window):
      
      if self.win.isClosed():
        self.CloseApp()
        
      width = self.win.getProperties().getXSize()
      height = self.win.getProperties().getYSize()
      
      lens = self.cam.node().getLens()
      lens.setFov(60)
      lens.setAspectRatio(width/height)
      
      lens.setFar(500.0)
      #lens.setFilmSize(width,height)
      #lens.setFocalLength(self.FOCAL_LENGTH)
      self.cam.node().setLens(lens)
      
      self.gui.onWindowEvent(window)
        
    def onKey(self, key, value):
        """Stores a value associated with a key."""
        self.keys[key] = value
        
        if self.keys['space']:
            self.speedBoost = not self.speedBoost
            self.gui.onSpeedBoostChanged(self.speedBoost)
        
    def onEscape(self):
        """Event when escape button is pressed."""
        
        # unfocus all
        for obj in self.HTMObjects.values():
            obj.DestroySynapses()
        
        
    def onMouseEvent(self, event,press):
        printLog("Mouse event:"+str(event),verbosityHigh)
        if event=='right':
            self.rotateCamera=press
            
            if self.mouseWatcherNode.hasMouse():
                self.mouseX_last = self.mouseWatcherNode.getMouseX()
                self.mouseY_last = self.mouseWatcherNode.getMouseY()
            else:
                self.mouseX_last = 0
                self.mouseY_last = 0
            """if press:
                props = WindowProperties()
                props.setCursorHidden(True)
                props.setMouseMode(WindowProperties.M_relative)
                self.win.requestProperties(props)"""
        elif event == 'left' and press:
          self.onClickObject()
        
    
    
    def updateHTMstate(self):
        if self.client.serverDataChange:
            self.client.serverDataChange=False
            printLog("Data change! Updating HTM state",verbosityMedium)
            
            serverObjs = self.client.serverData.HTMObjects
            
            # if we get HTM data objects, iterate over received data
            for obj in serverObjs:
                
                if not obj in self.HTMObjects:# its new HTM object
                    printLog("New HTM object arrived! Name:"+str(obj))
                    # create HTM object
                    newObj = cHTM(self.loader,obj)
                    newObj.getNode().reparentTo(self.render)
                    
                    #create inputs
                    for inp in serverObjs[obj].inputs:
                        newObj.CreateInput(name=inp,count=serverObjs[obj].inputs[inp].count,rows=int(math.sqrt(serverObjs[obj].inputs[inp].count)))
                   #create layers
                    for lay in serverObjs[obj].layers:
                        newObj.CreateLayer(name=lay,nOfColumnsPerLayer=serverObjs[obj].layers[lay].columnCount,nOfCellsPerColumn=serverObjs[obj].layers[lay].cellsPerColumn)
                        
                    self.HTMObjects[obj] = newObj
                # update HTM object
                
                # go through all incoming inputs
                for i in serverObjs[obj].inputs:#dict
                    #find matching input in local structure
                    
                    self.HTMObjects[obj].inputs[i].UpdateState(serverObjs[obj].inputs[i].bits,serverObjs[obj].inputs[i].stringValue)
            
                # go through all incoming layers
                for l in serverObjs[obj].layers:#dict
                    #find matching layer in local structure
                    self.HTMObjects[obj].layers[l].UpdateState(serverObjs[obj].layers[l].activeColumns,serverObjs[obj].layers[l].activeCells)
                
        if self.client.columnDataArrived:
            printLog("Column data arrived, updating synapses!",verbosityMedium)
            self.client.columnDataArrived=False
            serverObjs = self.client.serverData.HTMObjects
            
            for obj in serverObjs:
                
                self.HTMObjects[obj].DestroySynapses()
            
                for l in serverObjs[obj].layers:#dict
                    
                    printLog(serverObjs[obj].layers[l].proximalSynapses,verbosityHigh)
                    for syn in serverObjs[obj].layers[l].proximalSynapses:# array
                        
                        printLog("Layer:"+str(l),verbosityMedium)
                        printLog("proximalSynapses:"+str(syn),verbosityHigh)
                        
                        columnID = syn[0]
                        proximalSynapses = syn[1]
                        
                        #update columns with proximal Synapses
                        self.HTMObjects[obj].layers[l].corticalColumns[columnID].CreateProximalSynapses(serverObjs[obj].layers[l].proximalInputs,self.HTMObjects[obj].inputs,proximalSynapses)
                    
                    
         
            
            
#            inputData = self.client.serverData.inputs
#            inputDataSizes = self.client.serverData.inputDataSizes
#            inputsValueString = self.client.serverData.inputsValueString#just ordinary represented value that will be shown near input as string
#            
#            #UPDATES INPUTS
#            for i in range(len(inputData)):
#              if len(self.htmObject.inputs)<=i:#if no input instances exists
#                self.htmObject.CreateInput("IN"+str(i),count=inputDataSizes[i],rows=int(math.sqrt(inputDataSizes[i])))
#              
#              self.htmObject.inputs[i].UpdateState(inputData[i],inputsValueString[i])
#            
#            # UPDATES LAYERS
#            if len(self.htmObject.layers)==0:#if no input instances exists
#              self.htmObject.CreateLayer("SP/TM",nOfColumnsPerLayer=self.client.serverData.columnDimensions,nOfCellsPerColumn=self.client.serverData.cellsPerColumn)
#            printLog("Active columns:"+str(self.client.serverData.activeColumns),verbosityHigh)
#            self.htmObject.layers[0].UpdateState(activeColumns=self.client.serverData.activeColumns,activeCells=self.client.serverData.activeCells)
#          
#          if self.client.columnDataArrived and len(self.client.serverData.connectedSynapses)!=0:
#            self.client.columnDataArrived=False
#          
#            #if self.focusCursor!=None:
#            self.htmObject.DestroySynapses()
#            
#            self.focusCursor.column.CreateSynapses(self.htmObject.inputs,self.client.serverData.connectedSynapses)
#             
#            printLog("columnDataArrived",verbosityHigh)
        
        
        
    def update(self, task):
      
      """Updates the camera based on the keyboard input. Once this is
      done, then the CellManager's update function is called."""
      deltaT = globalClock.getDt()
      
      speed=self.speed
      
      if self.speedBoost:
          speed *=4
      
      """Rotation with mouse while right-click"""
      mw = self.mouseWatcherNode
      deltaX=0
      deltaY=0
      
      if mw.hasMouse() and self.rotateCamera:
          deltaX = mw.getMouseX() - self.mouseX_last
          deltaY = mw.getMouseY() - self.mouseY_last
          
          
          self.mouseX_last = mw.getMouseX()
          self.mouseY_last = mw.getMouseY()        
      
      if deltaT > 0.05:
        #FPS are low, limit deltaT
        deltaT=0.05
      
      move_x = deltaT * speed * -self.keys['a'] + deltaT * speed * self.keys['d']
      move_y = deltaT * speed * self.keys['s'] + deltaT * speed * -self.keys['w']
      self.move_z += deltaT * speed * self.keys['shift'] + deltaT * speed * -self.keys['control']
      
      self.camera.setPos(self.camera,move_x, -move_y, 0)
      self.camera.setZ(self.move_z)
      
      self.heading += (deltaT * 90 * self.keys['arrow_left'] +
                       deltaT * 90 * -self.keys['arrow_right'] +
                       deltaT * 5000 * -deltaX)
      self.pitch += (deltaT * 90 * self.keys['arrow_up'] +
                     deltaT * 90 * -self.keys['arrow_down']+
                     deltaT * 5000 * deltaY)
      self.camera.setHpr(self.heading, self.pitch, 0)
      
      
      self.updateHTMstate()
      
      
      return task.cont
        
    def CreateBasement(self):#it will create basement object, just for case that nothing is drawn to be not lost
        
        # Load the environment model.
        self.cube = self.loader.loadModel("models/cube")#/media/Data/Data/Panda3d/
        
        # Reparent the model to render.
        self.cube.reparentTo(self.render)
        # Apply scale and position transforms on the model.
        
        self.cube.setScale(10, 10, 10)
        self.cube.setPos(-8, -30, 0)
        
        self.cube.setColor(1.0,0,0,1.0)
        self.cube.setRenderModeThickness(5)
        
        self.cube.setRenderModeFilledWireframe(LColor(0,0,0,1.0))
        #COLLISION
        collBox = CollisionBox(self.cube.getPos(),10.0,10.0,10.0)
        cnodePath = self.cube.attachNewNode(CollisionNode('cnode'))
        cnodePath.node().addSolid(collBox)
        
        self.cube.setTag('clickable','1')
        

        
    def CreateTestScene(self):
        
        form = GeomVertexFormat.getV3()
        vdata = GeomVertexData('myLine',form,Geom.UHStatic)
        vdata.setNumRows(1)
        vertex = GeomVertexWriter(vdata,'vertex')
        
        vertex.addData3f(0,0,0)
        vertex.addData3f(60,0,50)
        
        prim = GeomLines(Geom.UHStatic)
        prim.addVertices(0,1)
        
        geom = Geom(vdata)
        geom.addPrimitive(prim)
        
        node = GeomNode('gnode')
        node.addGeom(geom)
        
        nodePath = self.render.attachNewNode(node)
        
        #self.HTMObjects.CreateInput("IN 1",count=500,rows=int(math.sqrt(500)))
        #self.HTMObjects.CreateLayer("SP/TM 1",nOfColumnsPerLayer=200,nOfCellsPerColumn=10)
        
    def HandlePickedObject(self,obj):
      printLog("PICKED OBJECT:"+str(obj),verbosityMedium)

      thisId = int(obj.getTag('clickable'))
      printLog("TAG:"+str(thisId),verbosityHigh)
      
      parent = obj.getParent()#skip LOD node
      tag = parent.getTag('id')
      if tag=="":
        printLog("Parent is not clickable!",verbosityHigh)
        return
      else:
        parentId = int(tag)
        printLog("PARENT TAG:"+str(parentId),verbosityHigh)
      
      
      if obj.getName() == 'cell':
        printLog("We clicked on cell",verbosityHigh)
        
        focusedHTMObject = str(obj).split('/')[1]
        focusedLayer = str(obj).split('/')[2]
        
        
        HTMObj = self.HTMObjects[focusedHTMObject]
        Layer = HTMObj.layers[focusedLayer]
        newCellFocus = Layer.corticalColumns[parentId].cells[thisId]
        self.focusedPath = [focusedHTMObject,focusedLayer];
        
        if self.focusedCell!=None:
          self.focusedCell.resetFocus()#reset previous
        self.focusedCell = newCellFocus
        self.focusedCell.setFocus()
        
        
        self.gui.focusedCell = self.focusedCell
        
        self.gui.focusedPath = self.focusedPath
        self.gui.columnID = Layer.corticalColumns.index(self.gui.focusedCell.column)
        
        self.gui.cmdGetColumnData=True
      elif obj.getName() == 'basement':
        self.testRoutine()
        
    def testRoutine(self):
        form = GeomVertexFormat.getV3()
        vdata = GeomVertexData('myLine',form,Geom.UHStatic)
        vdata.setNumRows(1)
        vertex = GeomVertexWriter(vdata,'vertex')
        
        vertex.addData3f(inputs[i].inputBits[y].getNode().getPos(self.__node))
        vertex.addData3f(-8,-30,0)
        
        prim = GeomLines(Geom.UHStatic)
        prim.addVertices(0,1)
        
        geom = Geom(vdata)
        geom.addPrimitive(prim)
        
        node = GeomNode('gnode')
        node.addGeom(geom)
        
        self.__columnBox.attachNewNode(node)
        
    def onClickObject(self):
      mpos = self.mouseWatcherNode.getMouse()
      self.pickerRay.setFromLens(self.camNode,mpos.getX(),mpos.getY())
      
      self.myTraverser.traverse(self.render)
      #assume for simplicity's sake that myHandler is a CollisionHandlerQueue
      if self.myHandler.getNumEntries()>0:
        #get closest object
        self.myHandler.sortEntries()
        
        pickedObj = self.myHandler.getEntry(0).getIntoNodePath()
        #printLog("----------- "+str(self.myHandler.getNumEntries()))
        print(self.myHandler.getEntries())
        pickedObj = pickedObj.findNetTag('clickable')
        print(pickedObj)
        if not pickedObj.isEmpty():
          self.HandlePickedObject(pickedObj)
          
        
if __name__ == "__main__":
    
  app = cApp()
  app.run()

