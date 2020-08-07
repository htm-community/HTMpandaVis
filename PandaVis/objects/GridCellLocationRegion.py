from .region import cRegion
from objects.gridCellModule import cGridCellModule


class cGridCellLocationRegion(cRegion):
  def __init__(self, name, cellData, gui):
    super().__init__(name, cellData, gui)

    self.gridCellModules = []

    self.gridCellModulesCount = self.parameters["moduleCount"]
    self.cellPerAxis = self.parameters["cellsPerAxis"]
    self.dimensions = self.parameters["dimensions"]

    for i in range(self.gridCellModulesCount):
      c = cGridCellModule(self.cellPerAxis)  # each with own scale and orientation
      self.gridCellModules.append(c)

    self.subObjects = self.gridCellModules

    self.SUBOBJ_DISTANCE_X = 0.2 * self.cellPerAxis
    self.SUBOBJ_DISTANCE_Y = 0.3 * self.cellPerAxis

  def getVerticalSize(self):
    return 3


  def UpdateState(self, regionData):  # regionData is cRegionData class from dataStructs.py
    return