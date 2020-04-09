# import sys
# from PyQt5.QtWidgets import QApplication, QWidget
# # QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)


import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget, QLCDNumber, QSlider, QVBoxLayout, QApplication)

def pt(asd):
    print(asd)

class SigSlot(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self)
        self.setWindowTitle('XXOO')
        lcd = QLCDNumber(self)
        slider = QSlider(Qt.Horizontal, self)

        vbox = QVBoxLayout()
        vbox.addWidget(lcd)
        vbox.addWidget(slider)

        self.setLayout(vbox)

        slider.valueChanged.connect(lcd.display)
        slider.valueChanged.connect(pt) # 其实就是函数回调
        self.resize(350, 250)


app = QApplication(sys.argv)
qb = SigSlot()
qb.show()
sys.exit(app.exec_())
