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
import objects.ConnectionFactory as ConnectionFactory

verbosityLow = 0
verbosityMedium = 1
verbosityHigh = 2
FILE_VERBOSITY = verbosityHigh  # change this to change printing verbosity of this file




def printLog(txt, verbosity=verbosityLow):
  if FILE_VERBOSITY >= verbosity:
    print(txt)


class cGridCellModule:
  def __init__(self, nOfCellsPerAxis):
    self.cells = []
    self.nOfCellsPerAxis = nOfCellsPerAxis
    self.cellCount = nOfCellsPerAxis*nOfCellsPerAxis
    self.CELL_OFFSET = 0.4 # space between cells


    for i in range(self.cellCount):
      self.cells.append(cCell(None))

    self.idx = -1

    self.transparency = 1.0
    self.gfxCreated = False
    self.LodDistance1Stored = 100.0
    self.LodDistance2Stored = 5000.0

    self.width = self.nOfCellsPerAxis * (1 + self.CELL_OFFSET) # width of the module


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



    self.__rhombusEnvelope = loader.loadModel(os.path.join(os.getcwd(), "models/rhombus"))
    self.__rhombusEnvelope.setPos(
      self.width/2, self.width/2, 0.0
    )


    self.__rhombusEnvelope.setScale(
      self.width/2, self.width/2, 0.5
    )
    self.__rhombusEnvelope.setName("columnBox")

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
    self.__rhombusEnvelope.reparentTo(self.__node)

    x = 0
    y = 0
    idx = 0
    for n in self.cells:
      n.CreateGfx(loader, idx)
      idx += 1

      pos = self._TransformRhombToGlob([x, y], 1+self.CELL_OFFSET, 0.0)

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

  def UpdateState(self, activeCells):
    for cellID in range(len(self.cells)):  # for each cell
      isActive = activeCells[cellID]

      self.cells[cellID].UpdateState(active=isActive, predictive=False, winner=False, focused=False,
                                     presynapticFocus=False,
                                     showPredictionCorrectness=False, prev_predictive=False)

  def getNode(self):
    return self.__node

  def updateWireframe(self, value):
    for cell in self.cells:
      cell.updateWireframe(value)
    if value:
      self.__rhombusEnvelope.setRenderModeFilledWireframe(LColor(0, 0, 0, 1.0))
    else:
      self.__rhombusEnvelope.setRenderModeFilled()


  def setTransparency(self, transparency):
    self.transparency = transparency
    for cell in self.cells:
      cell.setTransparency(transparency)


  def DestroySynapses(self, synapseType):
    if not self.gfxCreated:
      return
    for cell in self.cells:
      cell.DestroySynapses(synapseType)

    self.resetPresynapticFocus()

  def resetPresynapticFocus(self):
    if not self.gfxCreated:
      return
    for cell in self.cells:
      cell.resetPresynapticFocus()  # also reset distal focus

  def getDescription(self):
    txt = ""
    txt += "TODO GridCellModule desc ID:" + str(self.idx) + "\n"
    return txt
