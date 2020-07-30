from objects.region import cRegion
from objects.minicolumn import cMinicolumn

class cApicalTMPairRegion(cRegion):

    def __init__(self, name, cellData, gui):
        super().__init__(name, cellData, gui)

        self.columnCount = 240
        self.nOfCellsPerColumn = 10

        self.minicolumns = []

        for i in range(self.columnCount):
            c = cMinicolumn(name, self.nOfCellsPerColumn)
            self.minicolumns.append(c)

        self.subObjects = self.minicolumns

        self.SUBOBJ_DISTANCE_X = 8
        self.SUBOBJ_DISTANCE_Y = 2



    def getVerticalSize(self):
        return 3

    def UpdateState(self, regionData):
        super().UpdateState(regionData)

        for colID in range(len(self.minicolumns)):# go through all columns
            oneOfCellPredictive=False
            oneOfCellCorrectlyPredicted = False
            oneOfCellFalselyPredicted = False
            nOfActiveCells = 0

            for cellID in range(len(self.minicolumns[colID].cells)): # for each cell in column
                isActive = regionData.data["activeCells"][cellID+(colID*self.nOfCellsPerColumn)]#cellID+(colID*self.nOfCellsPerColumn) in regionData.data["activeCells"]
                isWinner = regionData.data["winnerCells"][cellID+(colID*self.nOfCellsPerColumn)]#cellID + (colID * self.nOfCellsPerColumn) in regionData.data["winnerCells"]
                isPredictive = regionData.data["next_predictedCells"][cellID+(colID*self.nOfCellsPerColumn)]#cellID+(colID*self.nOfCellsPerColumn) in regionData.data["next_predictedCells"]
                if self.gui.showPredictionCorrectness:
                    wasPredictive = regionData.data["predictedCells"][cellID+(colID*self.nOfCellsPerColumn)]#cellID+(colID*self.nOfCellsPerColumn) in regionData.data["predictedCells"]
                else:
                    wasPredictive = False

                if isPredictive:
                    oneOfCellPredictive=True

                if isActive:
                    nOfActiveCells = nOfActiveCells + 1


                self.minicolumns[colID].cells[cellID].UpdateState(active = isActive, predictive = isPredictive,winner = isWinner, showPredictionCorrectness = self.gui.showPredictionCorrectness, prev_predictive = wasPredictive)

                if self.gui.showPredictionCorrectness:
                    #get correct/false prediction info
                    if self.minicolumns[colID].cells[cellID].correctlyPredicted:
                        oneOfCellCorrectlyPredicted = True

                    if self.minicolumns[colID].cells[cellID].falselyPredicted:
                        oneOfCellFalselyPredicted = True

            if self.gui.showBursting and self.nOfCellsPerColumn>1: # not for layers with only 1 cell/column
                bursting = nOfActiveCells == self.nOfCellsPerColumn #if all cells in column are active -> the column is bursting

            else:
                bursting = False

            self.minicolumns[colID].UpdateState(bursting=bursting, activeColumn = False, oneOfCellPredictive=oneOfCellPredictive,
                                                    oneOfCellCorrectlyPredicted=oneOfCellCorrectlyPredicted, oneOfCellFalselyPredicted=oneOfCellFalselyPredicted)
