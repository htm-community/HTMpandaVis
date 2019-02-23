# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

from direct.showbase.ShowBase import ShowBase
from panda3d.core import LColor
from panda3d.core import GeomVertexFormat, GeomVertexData, GeomVertexWriter,Geom,GeomLines,GeomNode,PerspectiveLens

import socket, pickle
from enum import Enum
import _thread
import math
import numpy
import time
    
from htm import cHTM 
from gui import cGUI

inputData = []
inputDataChange = False
terminateClientThread = False

class cApp(ShowBase):
 
    FOCAL_LENGTH = 500
    
    def __init__(self):
        ShowBase.__init__(self)
        
        # Mouse and camera movement init
        self.mouseX_last=0
        self.mouseY_last=0
        self.rotateCamera=False
        self.move_z=50
        
    
        #self.CreateTestScene()
         

        self.SetupCameraAndKeys()

        self.taskMgr.add(self.update, 'main loop')
        
        self.accept(self.win.getWindowEvent(),self.onWindowEvent)
        
        
        #self.gui = cGUI()
        
        self.htm = cHTM(self.loader)
        
        self.htm.CreateLayer("L1",nOfColumnsPerLayer=20,nOfNeuronsPerColumn=3)
        
        self.htm.CreateLayer("L2",nOfColumnsPerLayer=20,nOfNeuronsPerColumn=3)
        
        
        
        #nOfLayers=3,nOfColumnsPerLayer=20,nOfNeuronsPerColumn=3
        
        self.htm.getNode().reparentTo(self.render)
        

    def SetupCameraAndKeys(self):
        # Setup controls
        self.keys = {}
        for key in ['arrow_left', 'arrow_right', 'arrow_up', 'arrow_down',
                    'a', 'd', 'w', 's','shift','control']:
            self.keys[key] = 0
            self.accept(key, self.push_key, [key, 1])
            self.accept('shift-%s' % key, self.push_key, [key, 1])
            self.accept('%s-up' % key, self.push_key, [key, 0])
        
        self.accept('escape', self.CloseApp, [])
        self.disableMouse()

        # Setup camera
        width = self.win.getProperties().getXSize()
        height = self.win.getProperties().getYSize()
        lens = PerspectiveLens()
        lens.setFov(60)

        lens.setAspectRatio(width/height)
        #lens.setFilmSize(width,height)
        #lens.setFocalLength(self.FOCAL_LENGTH)
        self.cam.node().setLens(lens)
        
        self.camera.setPos(40, -80, 0)
        self.heading = 0.0
        self.pitch = -30.0
        
        
        self.accept('mouse1',self.mouseEvent,["left",True])
        self.accept('mouse1-up',self.mouseEvent,["left",False])
        self.accept('mouse3',self.mouseEvent,["right",True])
        self.accept('mouse3-up',self.mouseEvent,["right",False])
        
    def CloseApp(self):
      global terminateClientThread
      print("CLOSE app event")
      __import__('sys').exit(0)
      terminateClientThread=True
      
    def onWindowEvent(self,window):
      
      if self.win.isClosed():
        self.CloseApp()
        
      width = self.win.getProperties().getXSize()
      height = self.win.getProperties().getYSize()
      
      lens = PerspectiveLens()
      lens.setFov(60)
      lens.setAspectRatio(width/height)
      
      
      #lens.setFilmSize(width,height)
      #lens.setFocalLength(self.FOCAL_LENGTH)
      self.cam.node().setLens(lens)
        
    def push_key(self, key, value):
        """Stores a value associated with a key."""
        self.keys[key] = value
        
    def mouseEvent(self, event,press):
        #print(event)
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
                
        
    def update(self, task):
      global inputDataChange
      """Updates the camera based on the keyboard input. Once this is
      done, then the CellManager's update function is called."""
      deltaT = globalClock.getDt()
      
      speed=20
      
      """Rotation with mouse while right-click"""
      mw = self.mouseWatcherNode
      deltaX=0
      deltaY=0
      
      if mw.hasMouse() and self.rotateCamera:
          deltaX = mw.getMouseX() - self.mouseX_last
          deltaY = mw.getMouseY() - self.mouseY_last
          
          
          self.mouseX_last = mw.getMouseX()
          self.mouseY_last = mw.getMouseY()        
      
      
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
      
      
      if len(inputData)!=0 and inputDataChange:
        inputDataChange=False
        
        for i in range(len(inputData)):
        
          if len(self.htm.inputs)<=i:#if no input is created
            self.htm.CreateInput("IN"+str(i),count=len(inputData[i]),rows=int(math.sqrt(len(inputData[i]))))
          
          self.htm.inputs[i].UpdateData(inputData[i])
        
        
        
        
      
      return task.cont
        
    
    def CreateTestScene(self):
        
        # Load the environment model.
        self.cube = self.loader.loadModel("cube")#/media/Data/Data/Panda3d/
        
        # Reparent the model to render.
        self.cube.reparentTo(self.render)
        # Apply scale and position transforms on the model.
        
        self.cube.setScale(10, 10, 10)
        self.cube.setPos(-8, 42, 0)
        
        self.cube.setColor(1.0,0,0,1.0)
        self.cube.setRenderModeThickness(5)
        
        self.cube.setRenderModeFilledWireframe(LColor(0,0,0,1.0))
        
        
        form = GeomVertexFormat.getV3()
        
        vdata = GeomVertexData('myLine',form,Geom.UHStatic)
        
        vdata.setNumRows(1)
        
        vertex = GeomVertexWriter(vdata,'vertex')
        
        vertex.addData3f(0,0,0)
        vertex.addData3f(0,0,10)
        
        prim = GeomLines(Geom.UHStatic)
        prim.addVertices(0,1)
        
        geom = Geom(vdata)
        geom.addPrimitive(prim)
        
        node = GeomNode('gnode')
        node.addGeom(geom)
        
        nodePath = self.render.attachNewNode(node)
        
        

class ClientData(object):
  def __init__(self):
    self.a = 0
    self.b = 0

class ServerData(object):
  def __init__(self):
    self.a = 0
    self.inputs = []
    
    
class CLIENT_CMD(Enum):
  QUIT = 0
  REQ_DATA = 1
  
class SERVER_CMD(Enum):
  SEND_DATA = 0
  NA = 1
  
  
def PackData(cmd,data):
  # Create an instance of ProcessData() to send to server.
  d = [cmd,data]
  # Pickle the object and send it to the server
  #protocol must be specified to be able to work with py2 on server side
  rawData = pickle.dumps(d,protocol=2)
 
  return rawData

def InitClient():
  _thread.start_new_thread( RunClient, () )

def RunClient():
  global inputDataChange,inputData,terminateClientThread
  
  HOST = 'localhost'
  PORT = 50007
  # Create a socket connection, keep trying if no success
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  connected=False
  
  while(not connected):
    try:
      s.connect((HOST, PORT))
      connected=True
    except Exception:
      time.sleep(1)
      continue
  
  print("Connected to server")
  
  while(not terminateClientThread):
    s.send(PackData(CLIENT_CMD.REQ_DATA,ClientData()))
    
    #print("Requested data")
    
    rxLen = 4096
    rxRawData=b''
    
    while(rxLen>=4096):
      partData = s.recv(4096)
      rxLen=len(partData)
      #print(rxLen)
      #print(type(partData))
      
      rxRawData = b''.join([rxRawData,partData])
      
      
    #print(rxRawData)
    #print(type(rxRawData))
    rxData = pickle.loads(rxRawData,encoding='latin1')
    
        
    if rxData[0]==SERVER_CMD.SEND_DATA:          
      #print(rxData[1].input)
      #print(type(rxData[1].input))
      inputData=rxData[1].inputs
      inputDataChange=True
    elif rxData[0]==SERVER_CMD.NA:
      print("Server has data not available")
      time.sleep(1)
    else:
      print("Unknown command:"+str(rxData[0]))
  
  
  variable = [CLIENT_CMD.QUIT]
  # Pickle the object and send it to the server
  #protocol must be specified to be able to work with py2 on server side
  rawData = pickle.dumps(variable,protocol=2)
  s.send(rawData)
    
  s.close()       
  print("ClientThread terminated")     
  
        
if __name__ == "__main__":
    
  InitClient()
  app = cApp()
  app.run()

