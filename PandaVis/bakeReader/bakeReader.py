# -*- coding: utf-8 -*-

from bakeReader.bakeReaderDatabase import Database
from bakeReader.dataStructs import cLinkData, cRegionData, cDataStream
from htm.bindings.algorithms import Connections

import numpy as np
import os
import time

#needed to gather distal synapses from dump
from htm.bindings.algorithms import TemporalMemory

class BakeReader(object):
    def __init__(self, databaseFilePath):
        self.databaseFilePath = databaseFilePath
        self.db = None

        self.regions = {}  # can contain cRegion instances
        self.links = {}  # can contain cLink instances
        self.dataStreams = {}  # can contain cDataStream instances

        self.tableNames = []

        self._reqProximalData = False
        self._reqDistalData = False
        
        self.cntIterations = 0

    def OpenDatabase(self):
        self.db = Database(self.databaseFilePath)  # connect to the database
        Log("Opening "+str(self.databaseFilePath))

        # load all table names to be able then to check if table exists quickly
        self.tableNames = self.db.getTableNames()

    def LoadParameters(self):
        regions = self.db.SelectAll('region_parameters', orderAscending = False) # reversed alphabetical order

        resultRegions = {}
        for region in regions:
            resultRegions[region['region']] = cRegionData(region['regionType'],region['parameters'])

        links = self.db.SelectAll('links')

        resultLinks = {}
        for link in links:
            resultLinks[link['id']] = cLinkData(link['sourceRegion'], link['sourceOutput'], link['destinationRegion'], link['destinationInput'])

        return resultRegions, resultLinks


    def BuildStructure(self):

        regions, links = self.LoadParameters()

        #each region has own tables of active cols, predictive cols etc..
        for regName, regData in regions.items():
            self.regions[regName] = regData

            Log("Region parameters loaded:"+str(regName))


        # load links
        self.links = links

        # figure out how many iterations there are

        self.cntIterations = self.LoadMaxIteration(next(x for x in self.tableNames if x.endswith("activeCells")))# get first region
        if self.cntIterations is None:
            raise RuntimeError("Database contains no data!")
        Log("Database contains data for "+str(self.cntIterations)+" iterations.")

    def LoadDataStreams(self):
        # DATA STREAMS - loaded all at once
        parStreamTables = [q for q in self.tableNames if q.startswith("dataStream_")]
        for streamTable in parStreamTables:
            streamName = streamTable.replace("dataStream_","")
            self.dataStreams[streamName] = cDataStream()
            Log("Loaded stream: " + streamName)

            data = self.db.SelectAll(streamTable)

            arr = np.empty(shape=(2,len(data)))
            i=0
            for d in data:#convert to numpy two dim array
                arr[0,i] = d['iteration']
                arr[1,i] = d['value']
                i=i+1


            self.dataStreams[streamName].allData = arr

    def LoadMaxIteration(self, tableName):
        row = self.db.SelectMaxIteration(tableName)
        return row
        

    # loads all tables for specified region
    # table name is like: "region__L2__activeCells"
    def LoadAllRegionData(self, region, iteration):
        regionTables = [i for i in self.tableNames if i.startswith("region__" + region)]

        for table in regionTables:
            row = self.db.SelectByIteration(table, iteration)
            self.regions[region].data[table.split("__")[2]] = row['data'] if row['data'] is not None else np.empty(0)

    # loads data from given region table to specified destDataName (to data dict)
    def LoadRegionData(self, region, iteration, databaseData, destDataName):
        tableName = "region__"+region+"__"+databaseData
        if tableName not in self.tableNames:
            return # requested table does not exists
        row = self.db.SelectByIteration(tableName, iteration)
        self.regions[region].data[destDataName] = row['data'] if row['data'] is not None else np.empty(0)

    def LoadPredictiveCells(self, region, iteration, loadPrevious=False):
        tableName = "region__"+region+"__predictedCells"

        if tableName not in self.tableNames:
            return  # table not exists

        row = self.db.SelectByIteration(tableName,iteration)
        if not loadPrevious:
            self.regions[region].predictiveCells = row['data'] if row['data'] is not None else np.empty(0)
        else:
            self.regions[region].prev_predictiveCells = row['data'] if row['data'] is not None else np.empty(0)

    def LoadConnections(self,connectionType, regionName, iteration): # loads connections (can be more then one)

        self.dumpFolderPath = os.path.splitext(self.databaseFilePath)[0] + "_dumpData"
        if connectionType != '':
            connectionType = "_" + connectionType
        try:
            with open(os.path.join(self.dumpFolderPath,str(regionName) + "_" + str(iteration)) + connectionType+".dump", "rb") as f:
                connections = Connections.load(f.read())
        except FileNotFoundError:
            connections = None
        return connections


    # used by Spatial pooler, loads connections that belongs to one column
    # connectionType - under what name it will by stored in internal data structure
    # connectionTypeFile - what is suffix of dump file with connections
    # regionName - region name
    # connectedOnly - loads only connected synapses
    def LoadColumnConnections(self, connectionType, connectionTypeFile, regionName, iteration, colID, connectedOnly):
        # note here "cells" means "columns" because Connection class is universal
        if colID==-1:
            return # this region doesn't have minicolumns
        connections = self.LoadConnections(connectionTypeFile, regionName, iteration)

        # gets presynaptic cells grouped by segments
        presynCells = self.getPresynapticCellsForCell(connections, colID, connectedOnly)

        found = False
        newConnType = False
        # if this column is already in the array, replace the data
        if connectionType in self.regions[regionName].columnConnections:
            for c in range(len(self.regions[regionName].columnConnections[connectionType])):
                if colID == self.regions[regionName].columnConnections[connectionType][c][0]:
                    self.regions[regionName].columnConnections[connectionType][c] = [colID, presynCells] # replacing
                    found = True
                    break
        else:
            newConnType = True
        if not found:
            if newConnType:# add new connection type
                self.regions[regionName].columnConnections[connectionType] = [[colID, presynCells]]
            else:# append data
                self.regions[regionName].columnConnections[connectionType] += [[colID, presynCells]]


    # loads connections that belongs to one cell
    def LoadCellConnections(self, connectionType, connectionTypeFile, regionName, iteration, cellID, connectedOnly):

        connections = self.LoadConnections(connectionTypeFile, regionName, iteration)
        if connections is None:
            return
        # gets presynaptic cells grouped by segments
        presynCells = self.getPresynapticCellsForCell(connections, cellID, connectedOnly)

        if connectionType in self.regions[regionName].cellConnections:# already present connectionType
            connType = self.regions[regionName].cellConnections[connectionType]
            # if this cell is already in the array, replace the data
            found = False
            for c in range(len(connType)):
                if cellID == connType[c][0]:# cellData
                    self.regions[regionName].cellConnections[connectionType][c] = [cellID, presynCells] # replacing
                    found = True
                    break

            if not found:
                self.regions[regionName].cellConnections[connectionType] += [[cellID, presynCells]] # appending
        else:
            # new connectionType
            self.regions[regionName].cellConnections[connectionType] = [[cellID, presynCells]] # appending to dict

    def CleanCellConnections(self, regionName):
        self.regions[regionName].cellConnections = {}

    def CleanColumnConnections(self, regionName):
        self.regions[regionName].columnConnections = {}

    # gets all presynaptic cells for specified cell
    def getPresynapticCellsForCell(self, connections, cellID, connectedOnly=False):
        #start_time = time.time()
        segments = connections.segmentsForCell(cellID)

        res = []

        for seg in segments:
            synapsesForSegment = connections.synapsesForSegment(seg)

            presynapticCells = []
            for syn in synapsesForSegment:

                if not connectedOnly or (connectedOnly and connections.permanenceForSynapse(syn) >= connections.connectedThreshold):
                    presynapticCells += [connections.presynapticCellForSynapse(syn)]
            res += [np.array(presynapticCells)]

        # if len(segments) > 0:
        # Log("getPresynapticCellsForCell() took %s ms " % ((time.time() - start_time)*1000))
        return res

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
    with open(os.path.join(os.getcwd(),"logs","pandaBaker.log"),"a") as file:
        file.write(dateStr+" >> "+str(s)+"\n")

