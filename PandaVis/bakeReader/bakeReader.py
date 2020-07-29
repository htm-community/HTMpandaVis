# -*- coding: utf-8 -*-

from bakeReader.bakeReaderDatabase import Database
from bakeReader.dataStructs import cLinkData, cRegionData

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

    def LoadParameters(self):
        regions = self.db.SelectAll('region_parameters')

        resultRegions = {}
        for region in regions:
            resultRegions[region['region']] = cRegionData(region['regionType'],region['parameters'])

        links = self.db.SelectAll('links')

        resultLinks = {}
        for link in links:
            resultLinks[link['id']] = cLinkData(link['sourceRegion'], link['sourceOutput'], link['destinationRegion'], link['destinationInput'])

        # load all table names to be able then to check if table exists quickly
        self.tableNames = self.db.getTableNames()

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
        self.cntIterations = self.LoadMaxIteration("region__"+next(iter(self.regions))+"__activeCells")# get first region
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


    # def LoadProximalSynapses(self, layer, columns, iteration):
    #     tableName = "layer_proximalSynapses_"+layer
    #     columnCount = self.layers[layer].params["sp_columnCount"]
    #     self.layers[layer].proximalSynapses = {} # erase dict
    #
    #     for col in columns: # what specific columns we want to get
    #         # we need to select by rowid, because of speed
    #         rowId = iteration * columnCount + col + 1
    #         row = self.db.SelectByRowId(tableName, rowId)
    #
    #         #now check for sure if the data fits
    #         if col != row['column'] or iteration != row['iteration']:
    #             raise RuntimeError("Data are not valid! Not sorted!")
    #         self.layers[layer].proximalSynapses[col] =  (row['data'] if row['data'] is not None else np.empty(0))# add to the dict
    #
    #
    # def LoadDistalSynapses(self, layer, column, cell, iteration):
    #     timeStartDistalSynapsesCalc = time.time()
    #     tm = TemporalMemory()
    #     tm.loadFromFile(os.path.join(os.path.splitext(self.databaseFilePath)[0] + "_distalDump",
    #                                      "" + str(layer) + "_" + str(iteration) + ".dump"))
    #
    #     reqCellID = int(column * self.layers[layer].params['tm_cellsPerColumn'] + cell)
    #
    #     print("requesting distals for cell:"+str(reqCellID))
    #     segments = self.getPresynapticCellsForCell(tm, reqCellID)
    #
    #     segNo = 0
    #     for seg in segments:  # for each segment
    #         if cell not in self.layers[layer].distalSynapses.keys():
    #             self.layers[layer].distalSynapses[cell] = {}
    #         self.layers[layer].distalSynapses[cell][segNo] = seg # add numpy array to the dict
    #         segNo += 1
    #
    #     return len(segments) > 0  # true if we got something for this cell

    def getPresynapticCellsForCell(self, tm, cellID):
        start_time = time.time()
        segments = tm.connections.segmentsForCell(cellID)

        # synapses = []
        res = []

        # if len(segments) > 0:
        # Log("segments len:"+str(len(segments)))
        for seg in segments:
            time1 = time.time()
            synapsesForSegment = tm.connections.synapsesForSegment(seg)
            # Log("synapsesForSegment() took %s ms " % ((time.time() - time1)*1000))
            # Log("synapses for segment len:" + str(len(segments)))
            # Log("datatype:" + str(type(synapsesForSegment)))
            # Log("synapsesForSegment len:" + str(len(synapsesForSegment)))

            # for syn in synapsesForSegment:
            # synapses += [syn]

            presynapticCells = []
            for syn in synapsesForSegment:
                # time2 = time.time()
                presynapticCells += [tm.connections.presynapticCellForSynapse(syn)]
                # Log("presynapticCellForSynapse() took %s ms " % ((time.time() - time2)*1000))
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

