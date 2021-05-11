#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Miyamoto! DX Level Editor - New Super Mario Bros. U Deluxe Level Editor
# Copyright (C) 2009-2021 Treeki, Tempus, angelsl, JasonP27, Kinnay,
# MalStar1000, RoadrunnerWMC, MrRean, Grop, AboodXD, Gota7, John10v10,
# mrbengtsson

# This file is part of Miyamoto! DX.

# Miyamoto! DX is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Miyamoto! DX is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Miyamoto! DX.  If not, see <http://www.gnu.org/licenses/>.

# firstRunWizard.py
# Cointains code for the first run wizard


################################################################
################################################################

import json
import os
from PyQt5 import QtGui, QtWidgets
import sys

from dialogs import PreferencesDialog
import globals
from misc import setting
from ui import SetAppStyle
from verifications import isValidGamePath, isValidObjectsPath


class PathPage(QtWidgets.QWizardPage):
    def __init__(self):
        super().__init__()

        self.pathLabel = QtWidgets.QLabel()
        self.pathLineEdit = QtWidgets.QLineEdit()

        self.pathButton = QtWidgets.QPushButton()
        self.pathButton.setDefault(False)
        self.pathButton.setFlat(False)

        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.addWidget(self.pathLabel)
        self.horizontalLayout.addWidget(self.pathLineEdit)
        self.horizontalLayout.addWidget(self.pathButton)

        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setItalic(True)
        font.setWeight(75)

        self.isValidLabel = QtWidgets.QLabel()
        self.isValidLabel.setFont(font)
        self.isValidLabel.setStyleSheet("color: rgb(255, 0, 0);")

        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout.addWidget(self.isValidLabel)

        self.setLayout(self.verticalLayout)

        self.pathLabel.setText("Path:")
        self.pathButton.setText("...")
        self.isValidLabel.setText("Invalid path!")

        self.isValid = False
        self.requireFinish = True
        self.isValidPathMethod = None

        self.pathLineEdit.textChanged.connect(self.isValidPath)
        self.pathButton.clicked.connect(self.openPath)

    def isValidPath(self):
        if not self.isValidPathMethod:
            return

        self.isValid = self.isValidPathMethod(self.pathLineEdit.text())
        if not self.isValid:
            self.isValidLabel.setText("Invalid path!")
            self.isValidLabel.setStyleSheet("color: rgb(255, 0, 0);")

        else:
            self.isValidLabel.setText("Path validated!")
            self.isValidLabel.setStyleSheet("color: rgb(0, 127, 0);")

        self.completeChanged.emit()

    def openPath(self):
        self.pathLineEdit.setText(QtWidgets.QFileDialog.getExistingDirectory(None, self.subTitle()))

    def isComplete(self):
        return self.isValid or not self.requireFinish


class GamePathPage(PathPage):
    def __init__(self):
        super().__init__()

        self.setTitle("Game Path (required)")
        self.setSubTitle(globals.trans.string('ChangeGamePath', 0, '[game]', globals.gamedef.name))

        self.isValidPathMethod = isValidGamePath

        path = globals.gamedef.GetGamePath()
        if path:
            self.pathLineEdit.setText(path)


class ObjectsPathPage(PathPage):
    def __init__(self):
        super().__init__()

        self.setTitle("Objects Path (optional)")
        self.setSubTitle("Choose the folder containing object folders")

        self.requireFinish = False
        self.isValidPathMethod = isValidObjectsPath

        path = setting('ObjPath')
        if path:
            self.pathLineEdit.setText(path)


ThemesTab = PreferencesDialog.getThemesTab(QtWidgets.QWizardPage)
class ThemesPage(ThemesTab):
    def __init__(self):
        super().__init__()

        self.setTitle("Set the theme (optional)")
        self.setSubTitle("Can be changed later from Miyamoto! Preferences\nYou have to launch the editor for the theme to apply")

        self.NonWinStyle.currentIndexChanged.connect(self.setStyle); self.setStyle()

    def setStyle(self):
        SetAppStyle(self.NonWinStyle.currentText())


class Wizard(QtWidgets.QWizard):
    def __init__(self):
        super().__init__()

        self.setWizardStyle(QtWidgets.QWizard.ClassicStyle)
        self.setOptions(QtWidgets.QWizard.IndependentPages|QtWidgets.QWizard.NoBackButtonOnStartPage)

        self.gamePathPage = GamePathPage()
        self.objectsPathPage = ObjectsPathPage()
        self.themesPage = ThemesPage()

        self.addPage(self.gamePathPage)
        self.addPage(self.objectsPathPage)
        self.addPage(self.themesPage)

        self.finished = False
        self.button(QtWidgets.QWizard.FinishButton).clicked.connect(self.finishClicked)

    def finishClicked(self):
        self.finished = True
