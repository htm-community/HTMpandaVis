from .region import cRegion
from objects.cell import cCell
from panda3d.core import TextNode

class cRawValuesRegion(cRegion):
  def __init__(self, name, cellData, gui):
    super().__init__(name, cellData, gui)

    self.OFFSET_Y = 10
    self.textNodes = []


  def CreateGfx(self, loader):
    super().CreateGfx(loader)
    for i in range(self.parameters["outputWidth"]):
      textNode = TextNode("RawValues test node "+str(i))
      textNode.setText("---")

      textNodePath = self._node.attachNewNode(textNode)
      textNodePath.setScale(5)

      textNodePath.setPos(0, self.OFFSET_Y*i, 0)

      self.textNodes.append(textNode)

  def UpdateState(self, regionData):# regionData is cRegionData class from dataStructs.py
    super().UpdateState(regionData)

    newValues = regionData.data["dataOut"]

    for i in range(len(self.textNodes)):
      self.textNodes[i].setText(str(newValues[i]))

  def getBoundingBoxSize(self):
    return [3, 1]  # [horizontal, vertical]



