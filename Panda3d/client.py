#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 26 02:56:29 2019

@author: osboxes
"""
import socket, pickle, struct
import _thread
import time
from dataExchange import ClientData,ServerData,CLIENT_CMD,SERVER_CMD


def PackData(cmd,data=[]):
    d = [cmd, data]
    # Pickle the object and send it to the server
    # protocol must be specified to be able to work with py2 on server side
    rawData = pickle.dumps(d, protocol=2)

    if len(rawData) % 4096 == 0:  # if length of data is multiple of chunck size
        # increase the data by 1 byte to prevent it - it causes problems in recv function
        # on the client side - because client doesn't know how long data to expect
        if isinstance(data, ServerData):
            data.compensateSize.append(1)  # increase size by some dummy bytes
            d = [cmd, data]
            rawData = pickle.dumps(d)#, protocol=2)
        else:
            print("Packed data is multiple of chunck size, but not known instance")

    return rawData

def send_one_message(sock, data):
    length = len(data)
    sock.sendall(struct.pack('!I', length))
    sock.sendall(data)

def recv_one_message(sock):
    lengthbuf = sock.recv(4)
    length, = struct.unpack('!I', lengthbuf)
    return sock.recv(length)


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
       
  
  def RunThread(self):
        
    HOST = 'localhost'
    PORT = 50007
    # Create a socket connection, keep trying if no success
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5)
    connected=False
    
    while(not connected):
      try:
        s.connect((HOST, PORT))
        connected=True
      except Exception:
        time.sleep(1)
        continue
    
    print("Connected to server:"+HOST+":"+str(PORT))
    
    #s.send(SocketClient.PackData(CLIENT_CMD.REQ_DATA))
    while(not self.terminateClientThread):
      #print("Sending REQ")
      send_one_message(s,PackData(CLIENT_CMD.REQ_DATA))
      
      if self.__gui.cmdRun:
        send_one_message(s,PackData(CLIENT_CMD.CMD_RUN))
        print("RUN req")
      elif self.__gui.cmdStop:
        send_one_message(s,PackData(CLIENT_CMD.CMD_STOP))
        print("STOP req")
      elif self.__gui.cmdStepForward:
        send_one_message(s,PackData(CLIENT_CMD.CMD_STEP_FWD))
        print("STEP")
      elif self.__gui.cmdGetColumnData:
        send_one_message(s,PackData(CLIENT_CMD.CMD_GET_COLUMN_DATA))
        print("GET COLUMN DATA")
      
      self.__gui.ResetCommands()
      
      print("data begin receiving")
      self.ReceiveData(s)
      print("data received")
    
    
    #send that we as a client are quitting
    send_one_message(s,PackData(CLIENT_CMD.QUIT))
    
    s.close()       
    print("ClientThread terminated")   

  def ReceiveData(self,s):
    rxRawData=b''
    try:
        rxRawData = recv_one_message(s)
#        while(rxLen>=4096):
#          partData = s.recv(4096)
#          rxLen=len(partData)
#          #print(rxLen)
#          #print(type(partData))
#          
#          rxRawData = b''.join([rxRawData,partData])
          
        print("lenRaw:"+str(len(rxRawData))) 
        print(rxRawData)
        
        #print(type(rxRawData))
        if len(rxRawData)==0:
            print("Received data are empty!")
            return
        rxData = pickle.loads(rxRawData,encoding='latin1')
        
        print("lenRx:"+str(len(rxData))) 
            
        print("RCV ID:"+str(rxData[0]))
        if len(rxData)>1:
            print("RCV data:"+str(rxData[1]))
            
        if rxData[0]==SERVER_CMD.SEND_DATA:          
          #print(rxData[1].input)
          #print(type(rxData[1].input))
          self.serverData=rxData[1]
          self.serverDataChange=True
          print("Data income")
        elif rxData[0]==SERVER_CMD.SEND_COLUMN_DATA: 
          self.serverData=rxData[1]
          self.columnDataArrived=True
          print("Column data arrived")
    
        elif rxData[0]==SERVER_CMD.NA:
          print("Server has data not available")
          time.sleep(1)
        else:
          print("Unknown command:"+str(rxData[0]))
          
    except socket.timeout:
        print("SocketTimeout")
        return
        