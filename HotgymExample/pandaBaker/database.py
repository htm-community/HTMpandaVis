# -*- coding: utf-8 -*-

import sqlite3
import numpy as np

# defining new SQLITE datatype to be able to store numpy array
def adapt_array(arr):
    return arr.tobytes()

def convert_array(text):
    return np.frombuffer(text)

sqlite3.register_adapter(np.array, adapt_array)
sqlite3.register_converter("array", convert_array)


class Database(object):
    def __init__(self,filePath):
        self.conn = sqlite3.connect(filePath,detect_types=sqlite3.PARSE_DECLTYPES)
        self.curs = self.conn.cursor()

    def CreateTable(self, tableName, columns):
        try:
            query = "CREATE TABLE " + tableName + " (%s);"%columns

            self.curs.execute(query)
            #self.conn.commit()

        except sqlite3.OperationalError:
            Log("Cannot create table " + tableName)

    @staticmethod
    def AddParanthesis(s):
        if type(s)==str:
            return "'"+s+"'"
        return s

    # inserts array of values into table
    def Insert(self,tableName, values):
        values = [Database.AddParanthesis(v) for v in values]
        try:
            query = "INSERT INTO " + tableName + " VALUES (%s);"%(",".join(values))

            self.curs.execute(query)

        except sqlite3.OperationalError:
            Log("Cannot insert values "+str(values)+" into table " + tableName)

    # inserts dictionary items into table with "name" and "value" column
    def InsertParameters(self,tableName, _dict):
        try:
            for i in _dict:
                query = "INSERT INTO " + tableName + " (name,value) VALUES (%s,%s);"%(Database.AddParanthesis(i),_dict[i])

                self.curs.execute(query)

        except sqlite3.OperationalError:
            Log("Cannot insert values "+str(_dict)+" into table " + tableName)

    def InsertDataArray(self, tableName,iteration, array):
        try:
            self.curs.execute("INSERT INTO " + tableName + " VALUES (?,?);",(iteration,array,))
            #self.conn.commit()

        except sqlite3.OperationalError:
            Log("Cannot insert values into table " + tableName)

    def InsertDataArray2(self, tableName, iteration, stringValue, array):
        try:
            self.curs.execute("INSERT INTO " + tableName + " VALUES (?,?,?);", (iteration, stringValue, array,))
            #self.conn.commit()

        except sqlite3.OperationalError:
            Log("Cannot insert values  into table " + tableName)


    def getTableNames(self):
        try:
            result = self.curs.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
            table_names = sorted(list(zip(*result))[0])

            return table_names
        except sqlite3.OperationalError:
            Log("Cannot get table names")
        
    def SelectTwo(self, tableName):
        try:
            self.curs.execute("SELECT * FROM " + tableName + ";")
            self.conn.commit()
            data = self.curs.fetchall()

            print(len(data))
            print(type(data[0][1]))
        except sqlite3.OperationalError:
            Log("Cannot select values from table " + tableName)




def Log(s):
    s = "SQLite:" + str(s)
    print(str(s))
    from datetime import datetime
    dateStr=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open("logs/database.log","a") as file:
        file.write(dateStr+" >> "+str(s)+"\n")
