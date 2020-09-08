
# this method calls callback 'createSynapse' for each synapse going from 'sourceRegion'. Using data 'connection' specified by 'idx'
# 'idx' can be cellID or colID
def CreateSynapses(callbackCreateSynapse, regionObjects, connections, idx ,sourceRegions ):
    lenOffset = 0
    for sourceRegion in sourceRegions:
        try:
            withMinicolumns = hasattr(regionObjects[sourceRegion], "minicolumns")
            withGridModules = hasattr(regionObjects[sourceRegion], "gridCellModules")
            foundMyData = False
            for arr in connections:
                # arr[0]# cellID (or ColumnID)
                # arr[1][0] # segment 0 cells
                # arr[1][1] # segment 1 cells
                if arr[0] == idx:
                    for segment in arr[1]:
                        for cell in segment:
                            if cell < lenOffset:
                                continue # skip if this is not for this input
                            cell -= lenOffset # substract len of previous inputs if there are more than one
                            if withMinicolumns:  # source region with minicolumns
                                colID = int(cell / regionObjects[sourceRegion].nOfCellsPerColumn)
                                cellID = int(cell % regionObjects[sourceRegion].nOfCellsPerColumn)

                                lenOffset_temp = len(regionObjects[sourceRegion].minicolumns[colID].cells)# to know if the below fails how much offset

                                presynCell = regionObjects[sourceRegion].minicolumns[colID].cells[cellID]
                            elif withGridModules:
                                modID = int(cell / regionObjects[sourceRegion].moduleCellCount)
                                cellID = int(cell % regionObjects[sourceRegion].moduleCellCount)

                                lenOffset_temp = len(regionObjects[sourceRegion].gridCellModules[modID].cells)# to know if the below fails how much offset

                                presynCell = regionObjects[sourceRegion].gridCellModules[modID].cells[cellID]
                            else:
                                lenOffset_temp = len(regionObjects[sourceRegion].cells)# to know if the below fails how much offset

                                presynCell = regionObjects[sourceRegion].cells[cell]

                            callbackCreateSynapse(presynCell)

                    foundMyData = True
                    break

            if not foundMyData:
                raise RuntimeError("Not found data for cell id:" + str(idx))
                break
        except IndexError:
            # this happens normally, when we try to get specific cell/column of input region, but it wasn't found on first,
            # try another input region
            lenOffset = lenOffset_temp
            continue