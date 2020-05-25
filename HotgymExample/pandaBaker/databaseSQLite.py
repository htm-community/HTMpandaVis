# -*- coding: utf-8 -*-

import sqlite3

import numpy as np


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

    def Insert(self,tableName, values):
        values = [Database.AddParanthesis(v) for v in values]
        try:
            query = "INSERT INTO " + tableName + " VALUES (%s);"%(",".join(values))

            self.curs.execute(query)
            #self.conn.commit()

        except sqlite3.OperationalError:
            Log("Cannot insert values "+str(values)+" into table " + tableName)

    def InsertDict(self,tableName, _dict):
        try:
            for i in _dict:
                query = "INSERT INTO " + tableName + " (name,value) VALUES (%s,%s);"%(Database.AddParanthesis(i),_dict[i])

                self.curs.execute(query)
                #self.conn.commit()

        except sqlite3.OperationalError:
            Log("Cannot insert values "+str(_dict)+" into table " + tableName)

    def InsertTwo(self, tableName,iteration, array):
        try:
            self.curs.execute("INSERT INTO " + tableName + " VALUES (?,?);",(iteration,array,))
            #self.conn.commit()

        except sqlite3.OperationalError:
            Log("Cannot insert values into table " + tableName)

    def InsertThree(self, tableName, iteration, stringValue, array):
        try:
            self.curs.execute("INSERT INTO " + tableName + " VALUES (?,?,?);", (iteration, stringValue, array,))
            #self.conn.commit()

        except sqlite3.OperationalError:
            Log("Cannot insert values  into table " + tableName)


    def SelectTwo(self, tableName):
        #try:
            self.curs.execute("SELECT * FROM " + tableName + ";")
            self.conn.commit()
            data = self.curs.fetchall()

            print(len(data))
            print(type(data[0][1]))
        #except sqlite3.OperationalError:
            #Log("Cannot select values from table " + tableName)

def getTXbuffer():
    data = []
    conn=sqlite3.connect('/home/pi/main.db')

    curs=conn.cursor()
    
    try:
        curs.execute("SELECT data,destination FROM TXbuffer;")# where destination = '"+destination+"';")
        conn.commit()
        
        data = curs.fetchall()
    except sqlite3.OperationalError:
        Log("Cannot read from database!")
        Log("SELECT data,destination FROM TXbuffer;")
        
    #now remove from database
    try:
        curs.execute("DELETE FROM TXbuffer;")# where destination = '"+destination+"';")
        conn.commit()
        
    except sqlite3.OperationalError:
        Log("Cannot delete from table TXbuffer!")

    return data


def getCmds():
    data = []
    conn = sqlite3.connect('/home/pi/main.db')

    curs = conn.cursor()

    try:
        curs.execute("SELECT updated,heatingInhibit,ventilationCmd,resetAlarm FROM cmd;")
        conn.commit()

        data = curs.fetchall()
    except sqlite3.OperationalError:
        Log("Cannot read from database!")
        Log("SELECT data,destination FROM cmd;")

    # now reset update flag from database
    try:
        curs.execute("UPDATE cmd SET updated=0, ventilationCmd=NULL, heatingInhibit=NULL, resetAlarm=NULL")
        conn.commit()

    except sqlite3.OperationalError:
        Log("Cannot reset update flag from table cmd!")

    if len(data) > 0 and len(data[0]) > 0 and data[0][0] != 0:  # update flag is true
        return data[0][1:]
    else:
        return None

def RemoveOnlineDevices():
    conn = sqlite3.connect('/home/pi/main.db')
    curs = conn.cursor()

    try:
        curs.execute("DELETE FROM onlineDevices;")
        conn.commit()

    except sqlite3.OperationalError:
        Log("Cannot remove online devices!")


def AddOnlineDevice(ipAddress):
    InsertValue("OnlineDevices", ipAddress)

def RemoveOnlineDevice(ipAddress):
    conn = sqlite3.connect('/home/pi/main.db')
    curs = conn.cursor()

    try:
        curs.execute("DELETE FROM onlineDevices WHERE ip = (?);", (ipAddress,))
        conn.commit()

    except sqlite3.OperationalError:
        Log("Cannot remove online device from table onlineDevices, ip:" + ipAddress)


def Log(s):
    s = "SQLite:" + str(s)
    print(str(s))
    from datetime import datetime
    dateStr=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open("logs/database.log","a") as file:
        file.write(dateStr+" >> "+str(s)+"\n")
