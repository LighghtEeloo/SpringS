import sys
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QCursor, QKeyEvent
from PyQt5.QtWidgets import (
    QLCDNumber, QSlider, QVBoxLayout, QHBoxLayout, 
    QWidget, QApplication, QFrame
)
QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)


class Mainwindow(QWidget):
    def __init__(self, parent=None, flags=Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)
        self.setWindowTitle('XXOO')
        self.resize(500,500)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainwindow = Mainwindow()
    mainwindow.show()
    sys.exit(app.exec_())


# def pt(asd):
#     print(asd)

# class SigSlot(QWidget):
#     def __init__(self, parent=None):
#         QWidget.__init__(self)
#         self.setWindowTitle('XXOO')
#         lcd = QLCDNumber(self)
#         slider = QSlider(Qt.Horizontal, self)

#         vbox = QVBoxLayout()
#         vbox.addWidget(lcd)
#         vbox.addWidget(slider)

#         self.setLayout(vbox)

#         slider.valueChanged.connect(lcd.display)
#         slider.valueChanged.connect(pt) # 其实就是函数回调
#         self.resize(350, 250)

# app = QApplication(sys.argv)
# qb = SigSlot()
# qb.show()
# sys.exit(app.exec_())
