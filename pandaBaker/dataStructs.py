# -*- coding: utf-8 -*-
import numpy as np
from htm.bindings.algorithms import TemporalMemory
from htm.advanced.algorithms.apical_tiebreak_temporal_memory import ApicalTiebreakPairMemory
import warnings


class cLayer(object):
    def __init__(self, sp=None, tm=None):
        # static vars ----------------------------------------------------------------------
        self.sp = sp
        self.tm = tm

        self.params =0#= Params(self.sp, self.tm)

        # to what inputs are the synapses connected
        self.proximalInputs = []  # [inputName1,inputName2,...]
        # to what distal connections are connected (exluding itself, so these are external distal)
        self.distalInputs = []  # [inputName1, inputName2] - can be input or layer



        # dynamic vars ----------------------------------------------------------------------
        self.activeColumns = np.empty(0)  # currently active columns (sparse) in this layer
        self.winnerCells = np.empty(0)
        self.activeCells = np.empty(0)
        self.predictiveCells = np.empty(0)

        # proximal synapses - contains values of permanences
        # dict of numpy arrays, e.g. proximalSynapses[0] is numpy array for column ID 0
        self.proximalSynapses = {}

        # synapses - contains values of permanences
        # dict of numpy arrays, e.g. distalSynapses[0] is numpy array for cell ID 0
        self.distalSynapses = {}


class cInput(object):
    def __init__(self, size):
        #static vars -----------
        if type(size)!=int:
            raise AttributeError("Input size must be integer!")
        self.size = size

        #dynamic vars ----------
        self.bits = np.empty(0)  # input SDRs (just indicies of active bits)
        self.stringValue = ""  # ordinary expressed value that is represented by input SDRs


class cDataStream(object):
    def __init__(self, dataType="REAL"):
        self.dataType = dataType
        self.value = None

        self.allData = None


