#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from objects.cell import cCell
from panda3d.core import NodePath, PandaNode, LODNode, LColor
from panda3d.core import (
  GeomVertexFormat,
  GeomVertexData,
  GeomVertexWriter,
  Geom,
  GeomLines,
  GeomNode,
)
from Colors import *

verbosityLow = 0
verbosityMedium = 1
verbosityHigh = 2
FILE_VERBOSITY = verbosityHigh  # change this to change printing verbosity of this file

CELL_OFFSET = 0.3


def printLog(txt, verbosity=verbosityLow):
  if FILE_VERBOSITY >= verbosity:
    print(txt)


class cGridCellModule:
  def __init__(self, nOfCellsPerAxis):
    self.cells = []
    for i in range(nOfCellsPerAxis*nOfCellsPerAxis):
      self.cells.append(cCell(self))

    self.idx = -1

    self.transparency = 1.0
    self.gfxCreated = False
    self.LodDistance1Stored = 100.0
    self.LodDistance2Stored = 5000.0


  def CreateGfx(self, loader, idx):
    #                __node
    #                /   \
    #  cellsNodePath   columnBox

    self.lod = LODNode("columnLOD")  # Level of detail node for Column
    self.__node = NodePath(
      self.lod
    )  # NodePath(PandaNode('column'))# loader.loadModel("models/box")
    self.__node.setPos(0, 0, 0)
    self.__node.setScale(1, 1, 1)

    self.idx = idx

    # self.__node.setTag('clickable',str(idx))#to be able to click on it

    self.__columnBox = loader.loadModel(os.path.join(os.getcwd(), "models/cube"))
    self.__columnBox.setPos(
      0, 0, -0.5 + (0 if len(self.cells) == 0 else len(self.cells) * (1 + CELL_OFFSET) / 2)
    )
    self.__columnBox.setScale(
      0.5, 0.5, 0.5 * (1 if len(self.cells) == 0 else len(self.cells) * (1 + CELL_OFFSET))
    )
    self.__columnBox.setName("columnBox")

    self.__cellsNodePath = NodePath(
      PandaNode("cellsNode")
    )  # to pack all cells into one node path
    self.__cellsNodePath.setName("column")
    self.__cellsNodePath.setTag(
      "id", str(idx)
    )  # to be able to retrieve index of column for mouse click

    self.lod.addSwitch(100.0, 0.0)
    self.lod.addSwitch(5000.0, 100.0)

    self.__cellsNodePath.reparentTo(self.__node)
    self.__columnBox.reparentTo(self.__node)

    z = 0
    idx = 0
    for n in self.cells:
      n.CreateGfx(loader, idx)
      idx += 1
      n.getNode().setPos(0, 0, z)
      z += 1 + CELL_OFFSET
      n.getNode().reparentTo(self.__cellsNodePath)

    self.gfxCreated = True

  def LODUpdateSwitch(self, lodDistance, lodDistance2):
    self.lodDistance1Stored = lodDistance
    self.lodDistance2Stored = lodDistance2

    self.lod.clearSwitches()
    self.lod.addSwitch(lodDistance, 0.0)
    self.lod.addSwitch(lodDistance2, lodDistance)

  def LODUpdateSwitch_long(self):
    self.lod.clearSwitches()
    self.lod.addSwitch(self.lodDistance2Stored, 0.0)
    self.lod.addSwitch(self.lodDistance2Stored, self.lodDistance2Stored)

  def LODUpdateSwitch_normal(self):
    self.LODUpdateSwitch(self.lodDistance1Stored, self.lodDistance2Stored)

  def UpdateState(self):
    pass

  def getNode(self):
    return self.__node

  def updateWireframe(self, value):
    for cell in self.cells:
      cell.updateWireframe(value)
    if value:
      self.__columnBox.setRenderModeFilledWireframe(LColor(0, 0, 0, 1.0))
    else:
      self.__columnBox.setRenderModeFilled()


  def setTransparency(self, transparency):
    self.transparency = transparency
    for cell in self.cells:
      cell.setTransparency(transparency)

    self.UpdateState()

  def DestroyProximalSynapses(self):
    if not self.gfxCreated:
      return
    for syn in self.__cellsNodePath.findAllMatches("ProximalSynapse"):
      syn.removeNode()

  def DestroyDistalSynapses(self):
    if not self.gfxCreated:
      return
    for cell in self.cells:
      cell.DestroyDistalSynapses()

    self.resetPresynapticFocus()

  def resetPresynapticFocus(self):
    if not self.gfxCreated:
      return
    for cell in self.cells:
      cell.resetPresynapticFocus()  # also reset distal focus

  def getDescription(self):
    txt = ""
    txt += "TODO:" + str(self.idx) + "\n"
    return txt
