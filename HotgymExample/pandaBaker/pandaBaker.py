# -*- coding: utf-8 -*-

from pandaBaker.database import Database
from pandaBaker.dataStructs import cHTMObject,cLayer,cInput
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
        self.db.CreateTable('connections', "htmObj TXT, input TEXT, layer TEXT, type TEXT")

        for obj in self.HTMObjects:
            self.db.CreateTable('par_inputs','htmObj TEXT, name TEXT, size INTEGER')
            for inp in self.HTMObjects[obj].inputs:
                self.db.Insert('par_inputs', [obj, inp, str(self.HTMObjects[obj].inputs[inp].size)])


            for ly in self.HTMObjects[obj].layers:
                tableName = 'par_'+obj + '_layers_' +ly
                self.db.CreateTable(tableName, "name TEXT, value REAL")
                #self.db.InsertParameters(tableName, self.HTMObjects[obj].layers[ly].spParams)
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

    def StoreIteration(self, iteration):
        for obj in self.HTMObjects:
            # store input states
            for inp in self.HTMObjects[obj].inputs:
                self.db.InsertDataArray2('inputs_'+inp, iteration, self.HTMObjects[obj].inputs[inp].stringValue, self.HTMObjects[obj].inputs[inp].bits)
            #layer states
            for ly in self.HTMObjects[obj].layers:
                self.db.InsertDataArray('layer_activeColumns_' + ly,
                                    iteration, self.HTMObjects[obj].layers[ly].activeColumns)
                self.db.InsertDataArray('layer_predictiveCells_' + ly,
                                    iteration, self.HTMObjects[obj].layers[ly].predictiveCells)
                self.db.InsertDataArray('layer_winnerCells_' + ly,
                                    iteration, self.HTMObjects[obj].layers[ly].winnerCells)
                self.db.InsertDataArray('layer_activeCells_' + ly,
                                    iteration, self.HTMObjects[obj].layers[ly].activeCells)

def Log(s):
    print(str(s))
    from datetime import datetime
    dateStr=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open("logs/pandaBaker.log","a") as file:
        file.write(dateStr+" >> "+str(s)+"\n")

