# -*- coding: utf-8 -*-
import numpy as np

def Params(sp, tm):

    spPars={}
    tmPars={}
    if sp is not None:

        sp_inputDims_x = sp.getInputDimensions()[0]
        sp_inputDims_y = sp.getInputDimensions()[1] if len(sp.getInputDimensions()) > 1 else 0
        sp_columnDimensions_x = sp.getColumnDimensions()[0]
        sp_columnDimensions_y = sp.getColumnDimensions()[1] if len(sp.getColumnDimensions()) > 1 else 0

        spPars = {'sp_inputDimensions_x': sp_inputDims_x,'sp_inputDimensions_y': sp_inputDims_y,
                'sp_columnDimensions_x': sp_columnDimensions_x, 'sp_columnDimensions_y': sp_columnDimensions_y,
                'sp_potentialPct': sp.getPotentialPct(), 'sp_potentialRadius': sp.getPotentialRadius(),
                'sp_globalInhibition': sp.getGlobalInhibition(), 'sp_localAreaDensity': sp.getLocalAreaDensity(),
                'sp_synPermInactiveDec': sp.getSynPermInactiveDec(), 'sp_synPermActiveInc': sp.getSynPermActiveInc(),
                'sp_synPermConnected': sp.getSynPermConnected(), 'sp_boostStrength': sp.getBoostStrength(),
                'sp_wrapAround': sp.getWrapAround()}

    if tm is not None:

        tmPars = {'tm_activationThreshold': tm.getActivationThreshold(),
                    'tm_cellsPerColumn': tm.getCellsPerColumn(),
                    'tm_initialPerm': tm.getInitialPermanence(),
                    'tm_maxSegmentsPerCell': tm.getMaxSegmentsPerCell(),
                    'tm_maxSynapsesPerSegment': tm.getMaxSynapsesPerSegment(),
                    'tm_minThreshold': tm.getMinThreshold(),
                    'tm_newSynapseCount': tm.getMaxNewSynapseCount(),
                    'tm_permanenceDec': tm.getPermanenceDecrement(),
                    'tm_permanenceInc': tm.getPermanenceIncrement()
                }

    return {**spPars, **tmPars}

class cLayer(object):
    def __init__(self, sp=None, tm=None):
        # static vars ----------------------------------------------------------------------
        self.sp = sp
        self.tm = tm

        self.params = Params(self.sp, self.tm)

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
        # array of numpy arrays, e.g. proximalSynapses[0] is numpy array for column ID 0
        self.proximalSynapses = [np.empty(0)]

        # synapses - contains values of permanences
        # array of numpy arrays, e.g. distalSynapses[0] is numpy array for cell ID 0
        self.distalSynapses = [np.empty(0)]


class cInput(object):
    def __init__(self, size):
        #static vars -----------
        self.size = size

        #dynamic vars ----------
        self.bits = np.empty(0)  # input SDRs (just indicies of active bits)
        self.stringValue = ""  # ordinary expressed value that is represented by input SDRs


