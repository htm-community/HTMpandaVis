# -*- coding: utf-8 -*-

from bakeReader.bakeReaderDatabase import Database
from bakeReader.dataStructs import cLayer,cInput
import numpy as np
import os

class BakeReader(object):
    def __init__(self, databaseFilePath):
        self.databaseFilePath = databaseFilePath
        self.db = None

        self.layers = {}  # can contain cLayer instances
        self.inputs = {}  # can contain cInput instances

        self._gui =None
        self._reqProximalData = False
        self._reqDistalData = False

    def OpenDatabase(self):
        self.db = Database(self.databaseFilePath)  # connect to the database

    def BuildStructure(self):
        tableNames = self.db.getTableNames()

        #build the structure, tables that start with par_
        parTables = [q for q in tableNames if q.startswith("par_") and q!='par_inputs']

        #each layer has own par table
        for t in parTables:
            ly = t.split('_')[2]
            self.layers[ly]=cLayer()
            Log("Loaded layer: " + ly)

            pars = self.db.SelectAll(t)
            # create dict from rows
            dictPars = {}
            for p in pars:
                dictPars[p['name']] = p['value']

            self.layers[ly].params = dictPars   # assign parameter dict to the layer
            Log("Layer parameters loaded:"+str(dictPars))

        #fill all inputs 
        rows = self.db.SelectAll('par_inputs')
        for row in rows:
            self.inputs[row['name']] = cInput(row['size'])
            Log("Loaded input : " + row['name'])

            # load connections
            connections = self.db.SelectAll("connections")

        for con in connections:
            if con["type"] == "proximal":
                self.layers[con["layer"]].proximalInputs.append(con["input"])
                Log("Loaded proximal input for layer: " + str(con["layer"]))
            elif con["type"] == "distal":
                self.layers[con["layer"]].distalInputs.append(con["input"])
                Log("Loaded distal input for layer: " + str(con["layer"]))


    def LoadInput(self, inp, iteration):
        tableName = "inputs_"+inp

        row = self.db.SelectByIteration(tableName,iteration)

        self.inputs[inp].bits = row['data']
        self.inputs[inp].stringValue = row['value']

    def LoadActiveColumns(self, layer, iteration):
        tableName = "layer_activeColumns_"+layer
        row = self.db.SelectByIteration(tableName,iteration)
        self.layers[layer].activeColumns = row['data'] if row['data'] is not None else np.empty(0)

    def LoadWinnerCells(self, layer, iteration):
        tableName = "layer_winnerCells_"+layer
        row = self.db.SelectByIteration(tableName,iteration)
        self.layers[layer].winnerCells = row['data'] if row['data'] is not None else np.empty(0)

    def LoadPredictiveCells(self, layer, iteration):
        tableName = "layer_predictiveCells_"+layer
        row = self.db.SelectByIteration(tableName,iteration)
        self.layers[layer].predictiveCells = row['data'] if row['data'] is not None else np.empty(0)

    def LoadActiveCells(self, layer, iteration):
        tableName = "layer_activeCells_"+layer
        row = self.db.SelectByIteration(tableName,iteration)
        self.layers[layer].activeCells = row['data'] if row['data'] is not None else np.empty(0)

    def LoadProximalSynapses(self, layer, columns, iteration):
        tableName = "layer_proximalSynapses_"+layer
        columnCount = self.layers[layer].params["sp_columnCount"]
        self.layers[layer].proximalSynapses = {} # erase dict

        for col in columns: # what specific columns we want to get
            # we need to select by rowid, because of speed
            rowId = iteration * columnCount + col + 1
            row = self.db.SelectByRowId(tableName, rowId)

            #now check for sure if the data fits
            if col != row['column'] or iteration != row['iteration']:
                raise RuntimeError("Data are not valid! Not sorted!")
            self.layers[layer].proximalSynapses[col] =  (row['data'] if row['data'] is not None else np.empty(0))# add to the dict


    #cellsPerColumn = self.bakeReader.layers[layerName].params["tm_cellsPerColumn"]
    #cellID = column*cellsPerColumn + cell

    def LoadDistalSynapses(self, layer, column, cell, iteration):
        tableName = "layer_distalSynapses_"+layer
        self.layers[layer].distalSynapses = {} # erase dict

        rows = self.db.SelectDistalData(tableName, iteration, column, cell) # get segments for this cell in this iteration

        segNo = 0
        for row in rows:# for each segment
            #now check for sure if the data fits
            if cell != row['cell'] or iteration != row['iteration']:
                raise RuntimeError("Data are not valid!")
            if cell not in self.layers[layer].distalSynapses.keys():
                self.layers[layer].distalSynapses[cell] = {}
            self.layers[layer].distalSynapses[cell][segNo] =  (row['data'] if row['data'] is not None else np.empty(0))# add to the dict

            segNo = segNo + 1

        return segNo>0 # true if we got something for this cell


    def setGui(self, gui):
        self._gui = gui

    def reqProximalData(self):
        self._reqProximalData = True

    def reqDistalData(self):
        self._reqDistalData = True

    def Close(self):
        self.db.Close()

def Log(s):
    print(str(s))
    from datetime import datetime
    dateStr=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open("logs/pandaBaker.log","a") as file:
        file.write(dateStr+" >> "+str(s)+"\n")

