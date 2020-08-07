#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import numpy as np
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

CELL_OFFSET = 0.4 # space between cells


def printLog(txt, verbosity=verbosityLow):
  if FILE_VERBOSITY >= verbosity:
    print(txt)


class cGridCellModule:
  def __init__(self, nOfCellsPerAxis):
    self.cells = []
    self.nOfCellsPerAxis = nOfCellsPerAxis


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

    width = self.nOfCellsPerAxis * (1 + CELL_OFFSET)/2

    self.__columnBox = loader.loadModel(os.path.join(os.getcwd(), "models/cube"))
    self.__columnBox.setPos(
      0.0,0.0,0.0#-width/2, -width/2, 0.0
    )


    self.__columnBox.setScale(
      width, width, 0.5
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

    x = 0
    y = 0
    idx = 0
    for n in self.cells:
      n.CreateGfx(loader, idx)
      idx += 1

      pos = self._TransformRhombToGlob([x, y], 1+CELL_OFFSET, 0.0)

      n.getNode().setPos(pos[0], pos[1], 0)


      x += 1
      if x >= self.nOfCellsPerAxis:
        y += 1
        x = 0

      n.getNode().reparentTo(self.__cellsNodePath)

    self.gfxCreated = True

    # transoforms coordinate system from rhombus to global
  def _TransformRhombToGlob(self, position, scale, orientation):
      t = np.radians(orientation)  # theta
      r = np.radians(60)  # rhombus skew
      s = scale

      # create Rotation Matrix
      R = np.array(((s * np.cos(t), s * np.cos(t + r)),
                    (s * np.sin(t), s * np.sin(t + r))))

      return np.matmul(R, position)  # multiply

  # transforms coordinate system from global to rhombus
  def _TransformGlobToRhomb(self, position, scale, orientation):
        t = np.radians(orientation)  # theta
        r = np.radians(60)  # rhombus skew
        s = scale
        # TODO add scale - use www.wolframalpha.com
        # create Rotation Matrix - inverse of the one in _TransformRhombToGlob()
        R = np.array(((np.sin(t + r) / np.sin(r), -np.cos(t + r) / np.sin(r)),
                      (-np.sin(t) / np.sin(r), np.cos(t) / np.sin(r))))

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
