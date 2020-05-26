# -*- coding: utf-8 -*-
import numpy as np

def SpatialPoolerParams(sp):
    if sp is None:
        return None

    sp_inputDims_x = sp.getInputDimensions()[0] if len(sp.getInputDimensions())>1 else sp.getInputDimensions()
    sp_inputDims_y = sp.getInputDimensions()[1] if len(sp.getInputDimensions()) > 1 else 0
    sp_columnDimensions_x = sp.getColumnDimensions()[0] if len(sp.getColumnDimensions()) > 1 else sp.getColumnDimensions()
    sp_columnDimensions_y = sp.getColumnDimensions()[1] if len(sp.getColumnDimensions()) > 1 else 0

    pars = {'sp_inputDimensions_x': sp_inputDims_x,'sp_inputDimensions_y': sp_inputDims_y,
            'sp_columnDimensions_x': sp_columnDimensions_x, 'sp_columnDimensions_y': sp_columnDimensions_y,
            'sp_potentialPct': sp.getPotentialPct(), 'sp_potentialRadius': sp.getPotentialRadius(),
            'sp_globalInhibition': sp.getGlobalInhibition(), 'sp_localAreaDensity': sp.getLocalAreaDensity(),
            'sp_synPermInactiveDec': sp.getSynPermInactiveDec(), 'sp_synPermActiveInc': sp.getSynPermActiveInc(),
            'sp_synPermConnected': sp.getSynPermConnected(), 'sp_boostStrength': sp.getBoostStrength(),
            'sp_wrapAround': sp.getWrapAround()}
    return pars

class cHTMObject(object):
    def __init__(self):
        self.layers = {}  # can contain cLayer instances
        self.inputs = {}  # can contain cInput instances

class cLayer(object):
    def __init__(self, sp=None, tm=None):
        # static vars ----------------------------------------------------------------------
        self.sp = sp
        self.spParams = SpatialPoolerParams(self.sp)

        self.tm = tm
        #self.tmParams = TemporalMemoryParams(self.tm)

        # to what inputs are the synapses connected
        self.proximalInputs = []  # [inputName1,inputName2,...]
        # to what distal connections are connected (exluding itself, so these are external distal)
        self.distalInputs = []  # [inputName1, inputName2] - can be input or layer



        # dynamic vars ----------------------------------------------------------------------
        self.activeColumns = np.empty(0)  # currently active columns (sparse) in this layer
        self.winnerCells = np.empty(0)
        self.activeCells = np.empty(0)
        self.predictiveCells = np.empty(0)

        #contains values of permanences
        # array - [[columnID_a,[destinationID_a1,destinationID_a2,...]],[columnID_b,[destinationID_b1,destinationID_b2,...]]]
        self.proximalSynapses = (
            []
        )  # first item in array is for what column, second is list of destination input bits

        # array - [colID, cellID,[destinationID1,destinationID2,...]]
        self.distalSynapses = (
            []
        )  # first item in array is for what column, second is list of destination cells in this layer


class cInput(object):
    def __init__(self, size):
        #static vars -----------
        self.size = 0

        #dynamic vars ----------
        self.bits = np.empty(0)  # input SDRs (just indicies of active bits)
        self.stringValue = ""  # ordinary expressed value that is represented by input SDRs


