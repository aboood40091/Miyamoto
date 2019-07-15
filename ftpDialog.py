import globals
import misc

from PyQt5 import QtCore, QtGui, QtWidgets

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
        if misc.setting('FtpHost', '') == '':
            dlg = FtpDialog()
            dlg.exec()
        
        return misc.setting('FtpHost', '') != ''

        
    def accept(self):
        self.saveSettings()
        super().accept()

    def loadSettings(self):
        self.host.setText(misc.setting('FtpHost', ''))
        self.port.setValue(int(misc.setting('FtpPort', '20')))
        self.user.setText(misc.setting('FtpUser', ''))
        self.pwd.setText(misc.setting('FtpPwd', ''))
        self.timeout.setValue(int(misc.setting('FtpTimeout', '3')))
        self.romfs.setText(misc.setting('FtpRomfs', '/atmosphere/titles/0100EA80032EA000/romfs/'))

    def saveSettings(self):
        misc.setSetting('FtpHost', self.host.text())
        misc.setSetting('FtpPort', self.port.value())
        misc.setSetting('FtpUser', self.user.text())
        misc.setSetting('FtpPwd', self.pwd.text())
        misc.setSetting('FtpTimeout', self.timeout.value())

        romfsPath = self.romfs.text()
        if not romfsPath.startswith('/'):
            romfsPath = '/' + romfsPath
        if not romfsPath.endswith('/'):
            romfsPath += '/'

        misc.setSetting('FtpRomfs', romfsPath)
