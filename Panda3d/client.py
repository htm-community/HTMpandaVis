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
    self.a = 0
    self.inputs = []
    self.activeColumnIndices=[]
    self.activeCells=[]
    self.columnDimensions=0
    self.cellsPerColumn=0
    
    
class CLIENT_CMD(Enum):
  QUIT = 0
  REQ_DATA = 1
  
class SERVER_CMD(Enum):
  SEND_DATA = 0
  NA = 1
  
  
class SocketClient():
  def __init__(self):
    
    _thread.start_new_thread( self.RunThread, () )
    
    self.serverData = None
    self.serverDataChange = False
    self.terminateClientThread = False
    
    
  @staticmethod
  def PackData(cmd,data):
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
    
    print("Connected to server")
    
    while(not self.terminateClientThread):
      s.send(SocketClient.PackData(CLIENT_CMD.REQ_DATA,ClientData()))
      
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
        self.serverData=rxData[1]
        self.serverDataChange=True
        #print("Data income")
  
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