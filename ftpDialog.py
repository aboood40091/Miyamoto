#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Miyamoto! DX Level Editor - New Super Mario Bros. U Deluxe Level Editor
# Copyright (C) 2009-2019 Treeki, Tempus, angelsl, JasonP27, Kinnay,
# MalStar1000, RoadrunnerWMC, MrRean, Grop, AboodXD, Gota7, John10v10

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


################################################################
################################################################

############ Imports ############

from PyQt5 import QtCore, QtGui, QtWidgets

import globals
from misc import setting, setSetting

#################################


class FtpDialog(QtWidgets.QDialog):
    def __init__(self, parent = None):
        super(FtpDialog, self).__init__(parent)

        self.setWindowTitle('FTP configuration - Miyamoto! v%s' % globals.MiyamotoVersion)

        layout = QtWidgets.QGridLayout(self)

        layout.addWidget(QtWidgets.QLabel("Host:"), 0, 0, QtCore.Qt.AlignRight)
        layout.addWidget(QtWidgets.QLabel("Port:"), 1, 0, QtCore.Qt.AlignRight)
        layout.addWidget(QtWidgets.QLabel("User:"), 2, 0, QtCore.Qt.AlignRight)
        layout.addWidget(QtWidgets.QLabel("Password:"), 3, 0, QtCore.Qt.AlignRight)
        layout.addWidget(QtWidgets.QLabel("Timeout:"), 4, 0, QtCore.Qt.AlignRight)
        layout.addWidget(QtWidgets.QLabel("Remote romfs path:"), 5, 0, QtCore.Qt.AlignRight)

        self.host = QtWidgets.QLineEdit()
        layout.addWidget(self.host, 0, 1)

        self.port = QtWidgets.QSpinBox()
        self.port.setRange(0, 65535)
        layout.addWidget(self.port, 1, 1)

        self.user = QtWidgets.QLineEdit()
        layout.addWidget(self.user, 2, 1)

        self.pwd = QtWidgets.QLineEdit()
        layout.addWidget(self.pwd, 3, 1)

        self.timeout = QtWidgets.QSpinBox()
        self.timeout.setRange(1, 60)
        layout.addWidget(self.timeout, 4, 1)

        self.romfs = QtWidgets.QLineEdit()
        layout.addWidget(self.romfs, 5, 1)

        self.buttonBox = QtWidgets.QDialogButtonBox()
        self.buttonBox.addButton("Ok", QtWidgets.QDialogButtonBox.AcceptRole)
        self.buttonBox.addButton("Cancel", QtWidgets.QDialogButtonBox.RejectRole)
        layout.addWidget(self.buttonBox, 6, 0, 1, 2)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.loadSettings()

        self.setFixedHeight(self.window().sizeHint().height())
        self.resize(600, self.height())

    @staticmethod
    def checkShow():
        if setting('FtpHost', '') == '':
            dlg = FtpDialog()
            dlg.exec()
        
        return setting('FtpHost', '') != ''

        
    def accept(self):
        self.saveSettings()
        super().accept()

    def loadSettings(self):
        self.host.setText(setting('FtpHost', ''))
        self.port.setValue(int(setting('FtpPort', '20')))
        self.user.setText(setting('FtpUser', ''))
        self.pwd.setText(setting('FtpPwd', ''))
        self.timeout.setValue(int(setting('FtpTimeout', '3')))
        self.romfs.setText(setting('FtpRomfs', '/atmosphere/titles/0100EA80032EA000/romfs/'))

    def saveSettings(self):
        setSetting('FtpHost', self.host.text())
        setSetting('FtpPort', self.port.value())
        setSetting('FtpUser', self.user.text())
        setSetting('FtpPwd', self.pwd.text())
        setSetting('FtpTimeout', self.timeout.value())

        romfsPath = self.romfs.text()
        if not romfsPath.startswith('/'):
            romfsPath = '/' + romfsPath
        if not romfsPath.endswith('/'):
            romfsPath += '/'

        setSetting('FtpRomfs', romfsPath)
