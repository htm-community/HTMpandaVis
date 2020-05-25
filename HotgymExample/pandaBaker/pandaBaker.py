# -*- coding: utf-8 -*-

from pandaBaker.databaseSQLite import Database
import numpy as np
import os

class PandaBaker(object):
    def __init__(self, databaseFilePath):
        self.databaseFilePath = databaseFilePath
        self.db = None
        self.HTMObjects = {}

    def PrepareDatabase(self):
        #create database file, delete if exists
        if os.path.exists(self.databaseFilePath):
            Log("database file "+self.databaseFilePath+" exists, deleting...")
            os.remove(self.databaseFilePath)
        else:
            Log("Creating new database file:"+self.databaseFilePath)

        self.db = Database(self.databaseFilePath)  # connect to the database


        # STATIC tables creation -----------------------------------------------------------------------------
        self.db.CreateTable('connections', "object TXT, input TEXT, layer TEXT, type TEXT")

        for obj in self.HTMObjects:
            self.db.CreateTable('par_inputs','htmObj TEXT, name TEXT, size INTEGER')
            for inp in self.HTMObjects[obj].inputs:
                self.db.Insert('par_inputs', [obj, inp, str(self.HTMObjects[obj].inputs[inp].size)])


            for ly in self.HTMObjects[obj].layers:
                tableName = 'par_'+obj + '_layers_' +ly
                self.db.CreateTable(tableName, "name TEXT, value REAL")
                self.db.InsertDict(tableName, self.HTMObjects[obj].layers[ly].spParams)
                #create table for defining to what inputs these layers are connected
                for pi in self.HTMObjects[obj].layers[ly].proximalInputs:
                    self.db.Insert("connections", [obj, pi, ly, 'proximal'])
                for pi in self.HTMObjects[obj].layers[ly].distalInputs:
                    self.db.Insert("connections", [obj, pi, ly, 'distal'])

        # DYNAMIC tables creation -----------------------------------------------------------------------------

        for inp in self.HTMObjects[obj].inputs:
            self.db.CreateTable('inputs_'+inp, "iteration INTEGER, value TEXT, data ARRAY")
        for ly in self.HTMObjects[obj].layers:
            self.db.CreateTable('layer_activeColumns_'+ly, "iteration INTEGER, data ARRAY")
            self.db.CreateTable('layer_predictiveCells_'+ly, "iteration INTEGER, data ARRAY")
            self.db.CreateTable('layer_winnerCells_'+ly, "iteration INTEGER, data ARRAY")
            self.db.CreateTable('layer_activeCells_'+ly, "iteration INTEGER, data ARRAY")

        self.db.conn.commit()

    def CommitBatch(self):# writes to the file, do it reasonably, it takes time
        self.db.conn.commit()

    def OpenDatabase(self):
        self.db = Database(self.databaseFilePath)  # connect to the database


    def TestSelect(self):
        self.db.SelectTwo('layer_activeColumns_SensoryLayer')

    def StoreIteration(self, iteration):
        for obj in self.HTMObjects:
            # store input states
            for inp in self.HTMObjects[obj].inputs:
                self.db.InsertThree('inputs_'+inp, iteration, self.HTMObjects[obj].inputs[inp].stringValue, self.HTMObjects[obj].inputs[inp].bits)
            #layer states
            for ly in self.HTMObjects[obj].layers:
                self.db.InsertTwo('layer_activeColumns_' + ly,
                                    iteration, self.HTMObjects[obj].layers[ly].activeColumns)
                self.db.InsertTwo('layer_predictiveCells_' + ly,
                                    iteration, self.HTMObjects[obj].layers[ly].predictiveCells)
                self.db.InsertTwo('layer_winnerCells_' + ly,
                                    iteration, self.HTMObjects[obj].layers[ly].winnerCells)
                self.db.InsertTwo('layer_activeCells_' + ly,
                                    iteration, self.HTMObjects[obj].layers[ly].activeCells)


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
    def __init__(self, sp, tm):
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

def Log(s):
    print(str(s))
    from datetime import datetime
    dateStr=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open("logs/pandaBaker.log","a") as file:
        file.write(dateStr+" >> "+str(s)+"\n")

