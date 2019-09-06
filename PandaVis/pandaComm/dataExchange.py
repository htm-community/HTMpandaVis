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
      
    self.HTMObjects = {} # dataHTMObject
    
    self.compensateSize=[]#to compensate size by dummy bytes 
    

# -------------------DATA OBJECTS ---------------------------------------------
# these data objects can be part of the serverData instance that is sent through
# the socket to the client
# client will determine what he can read by commands
    
class dataHTMObject(object):
    def __init__(self):
        self.layers = {} # dataLayer
        self.inputs = {} # dataInput
        
        
class dataLayer(object):
    def __init__(self,columnCount,cellsPerColumn):
        
        self.columnCount = columnCount
        self.cellsPerColumn = cellsPerColumn
        
        self.activeColumns=[] # currently active columns (sparse) in this layer
        self.activeCells=[]
        
        # two dims, [columnID,[destinationID1,...]]
        self.proximalSynapses = []  # first item in array is for what column, second is list of destination input bits
        
        # two dims, [columnID,[destinationID1,...]]
        self.distalSynapses = []  # first item in array is for what column, second is list of destination cells in this layer
        
        # three dims, [columnID,destinationLayerID, [destination_id1,...]]
        self.distalSynapses_external = []  # first item in array is for what column, second is list of destination cells in other layer
        
        
class dataInput(object):
    def __init__(self):
        self.count = 0
        self.bits = [] # input SDRs (just indicies of active bits)
        self.stringValue = [] # ordinary expressed value that is represented by input SDRs
           
        
        
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