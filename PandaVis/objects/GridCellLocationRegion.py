from .region import cRegion
from objects.gridCellModule import cGridCellModule


class cGridCellLocationRegion(cRegion):
  def __init__(self, name, cellData, gui):
    super().__init__(name, cellData, gui)

    self.gridCellModules = []

    self.gridCellModulesCount = 5;
    self.cellPerAxis = 10
    self.dimensions = 2

    if self.dimensions != 2:
      raise RuntimeError("Dimension of GridCellLocation Region must be 2!")

    for i in range(self.gridCellModulesCount):
      c = cGridCellModule(name)
      self.gridCellModules.append(c)

    self.subObjects = self.gridCellModules

    self.SUBOBJ_DISTANCE_X = 3
    self.SUBOBJ_DISTANCE_Y = 2

  def getVerticalSize(self):
    return 3


  def UpdateState(self, regionData):  # regionData is cRegionData class from dataStructs.py
    return