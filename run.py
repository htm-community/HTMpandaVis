# -*- coding: utf-8 -*-
import os
import sys
#change working directory to pandaVis folder
abspath = os.path.abspath(__file__)
workDir = os.path.dirname(abspath)
workDir = os.path.join(workDir,'PandaVis')
os.chdir(workDir)

sys.path.append(os.getcwd())

from entryWindow import cEntryWindow
from Explorer3D import cExplorer3D
from dashVis.dashVis import cDashVis
import threading

if __name__ == "__main__":
    entryWin = cEntryWindow()
    entryWin.Show()

    if entryWin.command == 'terminate':
        print("App terminated")

    if entryWin.command == '-runBoth-':
        print("RUN DASH in thread")
        dashVis = cDashVis()
        dashThread = threading.Thread(target=dashVis.run,args=(entryWin.databaseFilePath, entryWin.dashLayout), daemon=True)
        dashThread.start()

    if entryWin.command == '-runDash-':
        print("RUN DASH")
        dashVis = cDashVis()
        dashVis.run(entryWin.databaseFilePath, entryWin.dashLayout)

    if entryWin.command == '-run3Dexplorer-' or entryWin.command == '-runBoth-':
        print("RUN 3D explorer")
        app = cExplorer3D(entryWin.databaseFilePath)
        app.run()
        

        
        
    
