from .region import cRegion
from objects.cell import cCell

class cColumnPoolerRegion(cRegion):

    def __init__(self, name, cellData, gui):
        super().__init__(name, cellData, gui)

        self.cellCount = self.parameters["cellCount"]# 2048
        self.cells = []

        for i in range(self.cellCount):
            c = cCell(None)
            self.cells.append(c)

        self.subObjects = self.cells

        self.CELL_OFFSET = 0.4  # space between cells

        self.SUBOBJ_DISTANCE_X = 1 + self.CELL_OFFSET
        self.SUBOBJ_DISTANCE_Y = 1 + self.CELL_OFFSET


    def getVerticalSize(self):
        return 1

    def UpdateState(self, regionData):  # regionData is cRegionData class from dataStructs.py
        super().UpdateState(regionData)

        for cellID in range(len(self.cells)):  # for each cell
            isActive = regionData.data["activeCells"][cellID]

            self.cells[cellID].UpdateState(active=isActive, predictive=False, winner=False, focused=False,
                                           presynapticFocus=False,
                                           showPredictionCorrectness=False, prev_predictive=False)