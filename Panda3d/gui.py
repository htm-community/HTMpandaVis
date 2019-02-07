#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb  7 08:46:04 2019

@author: osboxes
"""

from direct.gui.DirectGui import DirectFrame

class cGUI:
     def __init__(self):
         self.myFrame = DirectFrame(frameColor = (0,0,0,0.3),frameSize=(-1,1,-1,1),
                                 pos=(1,-1,-1))
     