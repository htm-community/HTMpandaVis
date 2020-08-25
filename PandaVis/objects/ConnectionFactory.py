
def CreateSynapses(callbackCreateSynapse, regionObjects, cellConnections ,sourceRegion ,idx):
    withMinicolumns = hasattr(regionObjects[sourceRegion], "minicolumns")
    withGridModules = hasattr(regionObjects[sourceRegion], "gridCellModules")
    foundMyData = False
    for arr in cellConnections:
        # arr[0]# cellID
        # arr[1][0] # segment 0 cells
        # arr[1][1]  # segment 1 cells
        if arr[0] == idx:
            for segment in arr[1]:
                for cell in segment:
                    if withMinicolumns:  # region with minicolumns
                        colID = int(cell / regionObjects[sourceRegion].nOfCellsPerColumn)
                        cellID = int(cell % regionObjects[sourceRegion].nOfCellsPerColumn)
                        presynCell = regionObjects[sourceRegion].minicolumns[colID].cells[cellID]
                    elif withGridModules:
                        modID = int(cell / regionObjects[sourceRegion].moduleCellCount)
                        cellID = int(cell % regionObjects[sourceRegion].moduleCellCount)
                        presynCell = regionObjects[sourceRegion].gridCellModules[modID].cells[cellID]
                    else:
                        presynCell = regionObjects[sourceRegion].cells[cell]

                    callbackCreateSynapse(presynCell)

            foundMyData = True
            break

    if not foundMyData:
        raise RuntimeError("Not found data for cell id:" + str(idx))
