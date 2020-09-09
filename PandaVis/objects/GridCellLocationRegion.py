from .region import cRegion
from objects.gridCellModule import cGridCellModule


class cGridCellLocationRegion(cRegion):
  def __init__(self, name, cellData, gui):
    super().__init__(name, cellData, gui)

    self.gridCellModules = []

    self.gridCellModulesCount = self.parameters["moduleCount"]
    self.cellPerAxis = self.parameters["cellsPerAxis"]
    self.moduleCellCount = self.cellPerAxis*self.cellPerAxis
    self.dimensions = self.parameters["dimensions"]

    for i in range(self.gridCellModulesCount):
      c = cGridCellModule(self.cellPerAxis)  # each with own scale and orientation
      self.gridCellModules.append(c)

    self.subObjects = self.gridCellModules

    self.MODULE_OFFSET = c.width*0.2 # space between modules

    self.SUBOBJ_DISTANCE_X = c.width + self.MODULE_OFFSET # take some module width and add space between modules
    self.SUBOBJ_DISTANCE_Y = c.width + self.MODULE_OFFSET # take some module width and add space between modules


  def getBoundingBoxSize(self):
    return [(int)(self.MODULE_OFFSET*self.gridCellModulesCount), 1+10]  # [horizontal, vertical]


  def UpdateState(self, regionData):  # regionData is cRegionData class from dataStructs.py
    idx = 0
    moduleCellsCnt = self.cellPerAxis*self.cellPerAxis
    for module in self.gridCellModules:
      module.UpdateState(regionData.data["activeCells"][idx*moduleCellsCnt : moduleCellsCnt + idx*moduleCellsCnt]) # take over only appropriate active cells for each module
      idx+=1