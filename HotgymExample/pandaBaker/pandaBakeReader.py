# -*- coding: utf-8 -*-

from pandaBaker.database import Database
import numpy as np
import os

class PandaBakeReader(object):
    def __init__(self, databaseFilePath):
        self.databaseFilePath = databaseFilePath
        self.db = None
        self.HTMObjects = {}

    
    def OpenDatabase(self):
        self.db = Database(self.databaseFilePath)  # connect to the database

    def TestSelect(self):
        self.db.SelectTwo('layer_activeColumns_SensoryLayer')

    def BuildStructure(self):
        tableNames = self.db.getTableNames()

        #build the structure, tables that start with par_
        parTables = [q for q in tableNames if q.startswith("par_") and q!='par_inputs']
    
        #each layer has own par table
        for t in parTables:
            htmObj = f.split('_')[1]
            self.HTMObjects[htmObj] = cHTMObject()
            ly = f.split('_')[3]
            self.HTMObjects[htmObj].layers[ly]=cLayer()

        #fill all inputs 
        jj = self.db.SelectBlabla('par_inputs',htmObj)
        for i in inputs:
            self.HTMObjects[jj].inputs[i] = 


def Log(s):
    print(str(s))
    from datetime import datetime
    dateStr=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open("logs/pandaBaker.log","a") as file:
        file.write(dateStr+" >> "+str(s)+"\n")

