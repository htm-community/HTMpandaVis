#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 26 02:56:29 2019

@author: osboxes
"""
import socket, pickle
import _thread
import time
from dataExchange import ClientData,ServerData,CLIENT_CMD,SERVER_CMD
  
class SocketClient():
  def __init__(self):
    
    _thread.start_new_thread( self.RunThread, () )
    
    self.serverData = None
    self.serverDataChange = False
    self.terminateClientThread = False
    self.columnDataArrived = False
    
    self.__gui = None
    
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
      #print("Sending REQ")
      s.send(SocketClient.PackData(CLIENT_CMD.REQ_DATA))
      
      if self.__gui.cmdRun:
        s.send(SocketClient.PackData(CLIENT_CMD.CMD_RUN))
        print("RUN req")
      elif self.__gui.cmdStop:
        s.send(SocketClient.PackData(CLIENT_CMD.CMD_STOP))
        print("STOP req")
      elif self.__gui.cmdStepForward:
        s.send(SocketClient.PackData(CLIENT_CMD.CMD_STEP_FWD))
        print("STEP")
      elif self.__gui.cmdGetColumnData:
        s.send(SocketClient.PackData(CLIENT_CMD.CMD_GET_COLUMN_DATA))
        print("GET COLUMN DATA")
      
      self.__gui.ResetCommands()
      
      self.ReceiveData(s)
      #print("data received")
    
    
    #send that we as a client are quitting
    s.send(SocketClient.PackData(CLIENT_CMD.QUIT))
    
    s.close()       
    print("ClientThread terminated")   
    
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
    elif rxData[0]==SERVER_CMD.SEND_COLUMN_DATA: 
      self.serverData=rxData[1]
      self.columnDataArrived=True

    elif rxData[0]==SERVER_CMD.NA:
      print("Server has data not available")
      time.sleep(1)
    else:
      print("Unknown command:"+str(rxData[0]))
        