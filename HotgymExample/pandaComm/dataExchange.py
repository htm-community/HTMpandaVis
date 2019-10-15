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

        self.HTMObjects = {}  # dataHTMObject

        self.compensateSize = []  # to compensate size by dummy bytes


# -------------------DATA OBJECTS ---------------------------------------------
# these data objects can be part of the serverData instance that is sent through
# the socket to the client
# client will determine what he can read by commands


class dataHTMObject(object):
    def __init__(self):
        self.layers = {}  # dataLayer
        self.inputs = {}  # dataInput


class dataLayer(object):
    def __init__(self, columnCount, cellsPerColumn):

        self.columnCount = columnCount
        self.cellsPerColumn = cellsPerColumn

        self.activeColumns = []  # currently active columns (sparse) in this layer
        self.winnerCells = []
        self.predictiveCells = []

        # array - [[columnID_a,[destinationID_a1,destinationID_a2,...]],[columnID_b,[destinationID_b1,destinationID_b2,...]]]
        self.proximalSynapses = (
            []
        )  # first item in array is for what column, second is list of destination input bits

        # to what inputs are the synapses connected
        self.proximalInputs = []  # [inputName1,inputName2,...]

        # array - [colID, cellID,[destinationID1,destinationID2,...]]
        self.distalSynapses = (
            []
        )  # first item in array is for what column, second is list of destination cells in this layer

        # to what distal connections are connected (exluding itself, so these are external distal)
        self.distalInputs = [] # [inputName1, inputName2] - can be input or layer

class dataInput(object):
    def __init__(self):
        self.count = 0
        self.bits = []  # input SDRs (just indicies of active bits)
        self.stringValue = (
            []
        )  # ordinary expressed value that is represented by input SDRs


class CLIENT_CMD(Enum):
    QUIT = 0
    CMD_RUN = 1
    CMD_STOP = 2
    CMD_STEP_FWD = 3
    CMD_GET_STATE_DATA = 4
    CMD_GET_PROXIMAL_DATA = 5
    CMD_GET_DISTAL_DATA = 6


class SERVER_CMD(Enum):
    NA = 0
    SEND_STATE_DATA = 1
    SEND_PROXIMAL_DATA = 2
    SEND_DISTAL_DATA = 3
