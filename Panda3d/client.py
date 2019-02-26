#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 26 02:56:29 2019

@author: osboxes
"""
import socket, pickle
import _thread
import time
from enum import Enum

class ClientData(object):
  def __init__(self):
    self.a = 0
    self.b = 0

class ServerData(object):
  def __init__(self):
    self.inputsValueString = [] #ordinary expressed value that is represented by SDRs
    self.inputs = []
    self.activeColumnIndices=[]
    self.activeCells=[]
    self.columnDimensions=0
    self.cellsPerColumn=0
    
    
class CLIENT_CMD(Enum):
  QUIT = 0
  REQ_DATA = 1
  CMD_RUN = 2
  CMD_STOP = 3
  CMD_STEP_FWD = 4
  
class SERVER_CMD(Enum):
  SEND_DATA = 0
  NA = 1
  
  
class SocketClient():
  def __init__(self):
    
    _thread.start_new_thread( self.RunThread, () )
    
    self.serverData = None
    self.serverDataChange = False
    self.terminateClientThread = False
    
    self.gui = None
    
  def setGui(self,gui):
    self.__gui = gui
    
  @staticmethod
  def PackData(cmd,data=[]):
    # Create an instance of ProcessData() to send to server.
    d = [cmd,data]
    # Pickle the object and send it to the server
    #protocol must be specified to be able to work with py2 on server side
    rawData = pickle.dumps(d,protocol=2)
   
    return rawData
    
  
  def RunThread(self):
        
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
    
    print("Connected to server:"+HOST+":"+str(PORT))
    
    while(not self.terminateClientThread):
      s.send(SocketClient.PackData(CLIENT_CMD.REQ_DATA))
      
      if self.gui.cmdRun:
        s.send(SocketClient.PackData(CLIENT_CMD.CMD_RUN))
      elif self.gui.cmdStop:
        s.send(SocketClient.PackData(CLIENT_CMD.CMD_STOP))
      elif self.gui.cmdStepForward:
        s.send(SocketClient.PackData(CLIENT_CMD.CMD_STEP_FWD))
      
      self.gui.ResetCommands()
      
      #print("Requested data")
      self.ReceiveData(s)
    
    
    
    #send that we as a client are quitting
    s.send(SocketClient.PackData(CLIENT_CMD.QUIT))
    
  def ReceiveData(self,s):
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
      self.serverData=rxData[1]
      self.serverDataChange=True
      #print("Data income")

    elif rxData[0]==SERVER_CMD.NA:
      print("Server has data not available")
      time.sleep(1)
    else:
      print("Unknown command:"+str(rxData[0]))
      
    s.close()       
    print("ClientThread terminated")     