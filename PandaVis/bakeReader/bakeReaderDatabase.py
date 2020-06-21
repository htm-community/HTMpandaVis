# -*- coding: utf-8 -*-

import sqlite3
import numpy as np
import os
# defining new SQLITE datatype to be able to store numpy array types
#--------------------------------------------------------------------FLOAT ARRAY
def adapt_array(arr):
    return arr.tobytes()

def convert_array(text):
    return np.frombuffer(text,dtype=np.float32)

sqlite3.register_adapter(np.array, adapt_array)
sqlite3.register_converter("array", convert_array)
#--------------------------------------------------------------------SDR (SPARSE, contains active indicies)
def adapt_sdr(arr):
    return arr.tobytes()

def convert_sdr(text):
    return np.frombuffer(text,dtype=np.uint32)

sqlite3.register_adapter(np.array, adapt_sdr)
sqlite3.register_converter("sdr", convert_sdr)


class Database(object):
    def __init__(self,filePath):

        self.conn = sqlite3.connect(filePath,detect_types=sqlite3.PARSE_DECLTYPES)
        self.conn.row_factory = sqlite3.Row
        self.curs = self.conn.cursor()

    def CreateTable(self, tableName, columns):

        query = "CREATE TABLE " + tableName + " (%s);"%columns

        self.curs.execute(query)
        self.conn.commit()

    @staticmethod
    def AddParanthesis(s):
        if type(s)==str:
            return "'"+s+"'"
        return s

    # inserts array of values into table
    def Insert(self,tableName, values):
        values = [Database.AddParanthesis(v) for v in values]

        query = "INSERT INTO " + tableName + " VALUES (%s);"%(",".join(values))

        self.curs.execute(query)


    # inserts dictionary items into table with "name" and "value" column
    def InsertParameters(self,tableName, _dict):

        for i in _dict:
            query = "INSERT INTO " + tableName + " (name,value) VALUES (%s,%s);"%(Database.AddParanthesis(i),_dict[i])

            self.curs.execute(query)


    # insert into two column table
    def InsertDataArray(self, tableName,a, b):
        self.curs.execute("INSERT INTO " + tableName + " VALUES (?,?);",(a,b,))


    # insert into three column table
    def InsertDataArray2(self, tableName, a, b, c):

        self.curs.execute("INSERT INTO " + tableName + " VALUES (?,?,?);", (a, b, c,))




    def getTableNames(self):

        result = self.curs.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
        if(len(result)==0):
            raise RuntimeError("The database is empty!")
        table_names = sorted(list(zip(*result))[0])

        return table_names
        
    def SelectAll(self, tableName):

        self.curs.execute("SELECT * FROM " + tableName + ";")
        self.conn.commit()
        data = self.curs.fetchall()

        return data
    
    def SelectMaxIteration(self, tableName):
        self.curs.execute("SELECT MAX(iteration) FROM " + tableName + ";")
        self.conn.commit()
        data = self.curs.fetchone() # returns single row

        return data[0]
        
    # used on tables where iteration is unique value
    def SelectByIteration(self, tableName, iteration):

        self.curs.execute("SELECT * FROM " + tableName + " WHERE iteration=(?);",(iteration,))
        self.conn.commit()
        data = self.curs.fetchone() # returns single row

        return data

    def SelectByRowId(self, tableName, rowId):

        self.curs.execute("SELECT * FROM " + tableName + " WHERE rowid=(?);",(rowId,))
        self.conn.commit()
        data = self.curs.fetchone()#row id is unique

        return data

    def SelectDistalData(self, tableName, iteration, column, cell):

        self.curs.execute("SELECT * FROM " + tableName + " WHERE iteration = (?) AND column = (?) AND cell = (?);", (iteration,column,cell,))
        self.conn.commit()
        data = self.curs.fetchall()

        return data


    def Close(self):
        self.conn.close()




def Log(s):
    s = "SQLite:" + str(s)
    print(str(s))
    from datetime import datetime
    dateStr=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(os.path.join(os.getcwd(), "logs", "bakerDatabase.log"), "a") as file:
        file.write(dateStr+" >> "+str(s)+"\n")
