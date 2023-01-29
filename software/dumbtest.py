from PyQt5.QtWidgets import QApplication, QWidget

class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(0, 0, 1600, 1200)

    def mousePressEvent(self, event):
        print("Mouse clicked at", event.x(), event.y())
        


app = QApplication([])
widget = MyWidget()
widget.show()
app.exec_()

