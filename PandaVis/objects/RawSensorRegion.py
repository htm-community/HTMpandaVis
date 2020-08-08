from .region import cRegion
from objects.cell import cCell

class cRawSensorRegion(cRegion):
    def __init__(self, name, cellData, gui):
      super().__init__(name, cellData, gui)

      self.cellCount = 100
      self.cells = []

      for i in range(self.cellCount):
        c = cCell(None)
        self.cells.append(c)

      self.subObjects = self.cells

    def getVerticalSize(self):
      return 1

    def UpdateState(self, regionData):  # regionData is cRegionData class from dataStructs.py
      super().UpdateState(regionData)

      for cellID in range(len(self.cells)):  # for each cell
        isActive = regionData.data["dataOut"][cellID]

        self.cells[cellID].UpdateState(active=isActive, predictive=False, winner=False, focused=False,
                                       presynapticFocus=False,
                                       showPredictionCorrectness=False, prev_predictive=False)