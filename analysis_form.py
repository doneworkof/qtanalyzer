from PyQt5 import QtCore, QtGui, QtWidgets
from threading import Thread
from time import sleep
from PIL.ImageQt import ImageQt


class AnalysisDisplay(object):
    def __init__(self, col_name, results):
        super(AnalysisDisplay, self).__init__()
        self.results = results
        self.col_name = col_name

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setFixedSize(675, 401)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(10, 10, 571, 31))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.listWidget = QtWidgets.QListWidget(self.centralwidget)
        self.listWidget.setGeometry(QtCore.QRect(10, 50, 211, 341))
        self.listWidget.setObjectName("listWidget")

        for key in self.results:
            item = QtWidgets.QListWidgetItem(key)
            self.listWidget.addItem(item)
        
        self.listWidget.setCurrentRow(0)
        self.listWidget.itemSelectionChanged.connect(self.on_transition)

        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(550, 370, 111, 23))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(MainWindow.close)
        self.content_buffer = QtWidgets.QLabel(self.centralwidget)
        self.content_buffer.setGeometry(QtCore.QRect(240, 60, 421, 301))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.content_buffer.setFont(font)
        self.content_buffer.setText("")
        self.content_buffer.setScaledContents(False)
        self.content_buffer.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.content_buffer.setObjectName("content_buffer")
        self.content_buffer.setWordWrap(True)
        MainWindow.setCentralWidget(self.centralwidget)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.results = {
            key: (val if type(val) == str else self.adapt(val[0]))
            for key, val in self.results.items()
        }
        self.keys = list(self.results.keys())
        self.values = list(self.results.values())

        self.update_content()

    def wait_and_update(self):
        sleep(.1)
        self.update_content()

    def adapt(self, img):
        max_width_growth = self.content_buffer.width() / img.size[0]
        max_height_growth = self.content_buffer.height() / img.size[1]
        growth = min(max_width_growth, max_height_growth)
        new_width = int(img.size[0] * growth)
        new_height = int(img.size[1] * growth)
        return ImageQt(img.resize((new_width, new_height)))

    def on_transition(self):
        t = Thread(target=self.wait_and_update)
        t.start()

    def update_content(self):
        i = self.listWidget.currentRow()
        content = self.values[i]
        if type(content) == str:
            self.content_buffer.setPixmap(QtGui.QPixmap())
            self.content_buffer.setText(content)
        else:
            self.content_buffer.setText('')
            self.content_buffer.setPixmap(
                QtGui.QPixmap.fromImage(content))

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Статистика"))
        self.label.setText(_translate("MainWindow", f"Статистика колонки \"{self.col_name}\""))
        self.pushButton.setText(_translate("MainWindow", "Закрыть"))


if __name__ == "__main__":
    import sys

    n = 1000
    col = pd.Series(np.random.randn(n) * 100)
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow('COLUMN', NumAnalyzer(col).results)
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
