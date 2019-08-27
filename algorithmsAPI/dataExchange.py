#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 28 02:33:11 2019

@author: osboxes
"""
from enum import Enum

class ClientData(object):
  def __init__(self):
    self.a = 0
    self.b = 0

class ServerData(object):
  def __init__(self):
    self.inputsValueString = [] #ordinary expressed value that is represented by input SDRs
    self.inputs = [] # input SDRs (just indicies of active bits)
    self.activeColumns=[] # activeColumns
    self.activeCells=[]
    self.inputDataSizes=[]
    self.columnDimensions=0
    self.cellsPerColumn=0
    self.connectedSynapses=[]
    
    self.compensateSize=[]#to compensate size by dummy bytes
   
    
class CLIENT_CMD(Enum):
  QUIT = 0
  REQ_DATA = 1
  CMD_RUN = 2
  CMD_STOP = 3
  CMD_STEP_FWD = 4
  CMD_GET_COLUMN_DATA = 5
  
class SERVER_CMD(Enum):
  NA = 0
  SEND_DATA = 1
  SEND_COLUMN_DATA = 2