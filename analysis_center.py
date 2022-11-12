from PyQt5 import QtCore, QtGui, QtWidgets
from analysis import *
from tools import *
import pandas as pd
from analysis_form import AnalysisDisplay
import os


class AnalysisCenter(object):
    def __init__(self, df, current_col, states, classes):
        super(AnalysisCenter, self).__init__()
        self.current_col = current_col
        others = dict()
        for i, col in enumerate(df.columns):
            if col == current_col:
                current_class = classes[i]
                continue
            elif states[i]:

                others[col] = classes[i]
        
        results = dict()

        if current_class in [NUMERIC, CATEGORICAL]:
            results[f'Анализ колонки "{current_col}"'] = {
                NUMERIC: NumAnalyzer,
                CATEGORICAL: CatAnalyzer
            }[current_class](df[current_col])

        for col, class_ in others.items():
            label = f'Взаимосвязь колонок "{current_col}" и "{col}"'
            if class_ == current_class == CATEGORICAL:
                results[label] = CatCatAnalyzer(df[current_col], df[col])
            elif class_ == CATEGORICAL and current_class == NUMERIC:
                results[label] = NumCatAnalyzer(df[current_col], df[col])
            elif class_ == NUMERIC and current_class == CATEGORICAL:
                results[label] = NumCatAnalyzer(df[col], df[current_col])
            elif class_ == current_class == NUMERIC:
                results[label] = NumNumAnalyzer(df[current_col], df[col])

        self.keys = list(results.keys())
        self.analysers = list(results.values())

    def setupUi(self, MainWindow):
        self.win = MainWindow
        MainWindow.setObjectName("MainWindow")
        MainWindow.setFixedSize(440, 231)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(10, 10, 421, 31))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.components = QtWidgets.QListWidget(self.centralwidget)
        self.components.setGeometry(QtCore.QRect(10, 50, 421, 131))
        self.components.setObjectName("components")

        for k in self.keys:
            item = QtWidgets.QListWidgetItem(k)
            self.components.addItem(item)

        self.components.setCurrentRow(0)

        self.open = QtWidgets.QPushButton(self.centralwidget)
        self.open.setGeometry(QtCore.QRect(310, 200, 121, 21))
        self.open.setObjectName("open")
        self.open.clicked.connect(self.open_analysis)
        self.save_all = QtWidgets.QPushButton(self.centralwidget)
        self.save_all.setGeometry(QtCore.QRect(160, 200, 111, 23))
        self.save_all.setObjectName("save_all")
        self.save_all.clicked.connect(self.save_analysis)
        self.back = QtWidgets.QPushButton(self.centralwidget)
        self.back.setGeometry(QtCore.QRect(10, 200, 111, 23))
        self.back.setObjectName("back")
        self.back.clicked.connect(MainWindow.close)
        MainWindow.setCentralWidget(self.centralwidget)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def save_analysis(self):
        path = str(QtWidgets.QFileDialog.getExistingDirectory(
            parent=self.win,
            caption='Выберите папку для сохранения анализа',
            directory=os.getcwd()))
        if not path:
            return
        for k, a in zip(self.keys, self.analysers):
            new_folder = path + '/' + replace_forbidden_symbols(k)
            if not os.path.exists(new_folder):
                os.mkdir(new_folder)
            a.save(new_folder + '/')


    def open_analysis(self):
        a = self.analysers[self.components.currentRow()]
        self.win = QtWidgets.QMainWindow()
        self.win_ui = AnalysisDisplay(self.current_col, a.results)
        self.win_ui.setupUi(self.win)
        self.win.show()

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Компоненты анализа"))
        self.label.setText(_translate("MainWindow", f"Анализ колонки \"{self.current_col}\""))
        self.open.setText(_translate("MainWindow", "Открыть"))
        self.save_all.setText(_translate("MainWindow", "Сохранить всё"))
        self.back.setText(_translate("MainWindow", "Закрыть"))


if __name__ == "__main__":
    import sys
    n = 1000
    col = pd.Series(np.random.randn(n) * 100)
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = AnalysisComponents('COLUMN', {'Анализ колонки': NumAnalyzer(col)})
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
