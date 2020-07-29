from .region import cRegion

class cGridCellLocationRegion(cRegion):
  def __init__(self, name, cellData, gui):
    super().__init__(name, cellData, gui)

  def getVerticalSize(self):
    return 10


  def UpdateState(self, regionData):  # regionData is cRegionData class from dataStructs.py
    return