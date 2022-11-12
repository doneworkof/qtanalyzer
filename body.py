from PyQt5 import QtCore, QtGui, QtWidgets
from tools import *
import os
from analysis_center import AnalysisCenter
import sqlite3


LABEL_LEN = 44
MIN_GAP = 5
TARGET_COLOR = '#ffeb36'


class BodyWindow(object):
    def __init__(self, df, path, f, root):
        self.root_class = root
        self.df = df
        self.path = path
        self.df_name = extract_name(path)
        self.available_formats = ['SQLITE', 'XLSX', 'CSV']
        self.available_formats.remove(f.upper())
        self.types = [choose_type(df[col]) for col in df.columns]
    
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setFixedSize(614, 333)
        self.win = MainWindow
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.columns = QtWidgets.QListWidget(self.centralwidget)
        self.columns.setGeometry(QtCore.QRect(10, 60, 421, 261))
        self.columns.setFont(QtGui.QFont('Consolas', 14))
        self.columns.setObjectName("columns")
        self.states = [False] * len(self.df.columns)

        for i, col in enumerate(self.df.columns):
            self.add_column(col, self.types[i])

        self.columns.setCurrentRow(0)

        self.save = QtWidgets.QPushButton(self.centralwidget)
        self.save.setGeometry(QtCore.QRect(450, 120, 101, 23))
        self.save.setObjectName("save")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(450, 60, 151, 21))
        self.label.setObjectName("label")
        self.format_choice = QtWidgets.QComboBox(self.centralwidget)
        self.format_choice.setGeometry(QtCore.QRect(450, 90, 151, 22))
        self.format_choice.setObjectName("format_choice")
        self.format_choice.addItems(self.available_formats)
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(450, 160, 151, 21))
        self.label_2.setObjectName("label_2")
        self.make_analysis = QtWidgets.QPushButton(self.centralwidget)
        self.make_analysis.setGeometry(QtCore.QRect(450, 190, 151, 23))
        self.make_analysis.setObjectName("make_analysis")
        self.make_analysis.clicked.connect(self.analyse)
        self.toggle_target = QtWidgets.QPushButton(self.centralwidget)
        self.toggle_target.setGeometry(QtCore.QRect(450, 220, 151, 23))
        self.toggle_target.setObjectName("toggle_target")
        self.toggle_target.clicked.connect(self.on_toggle_target)
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(10, 20, 391, 28))
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(450, 286, 131, 31))
        self.label_4.setWordWrap(True)
        self.label_4.setObjectName("label_4")
        font = QtGui.QFont()
        font.setPointSize(16)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.reload = QtWidgets.QPushButton(self.centralwidget)
        self.reload.setGeometry(QtCore.QRect(450, 250, 151, 23))
        self.reload.setObjectName("reload")
        self.reload.clicked.connect(self.on_reload)
        MainWindow.setCentralWidget(self.centralwidget)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        self.save.clicked.connect(self.save_as)

    def on_reload(self):
        self.root = QtWidgets.QMainWindow()
        self.root_ui = self.root_class()
        self.root_ui.setupUi(self.root)
        self.root.show()
        self.win.close()

    def save_as(self):
        f = self.format_choice.currentText().lower()
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self.win, 'Сохраните таблицу', os.getcwd(), filter=f'{f.upper()} files (*.{f})')
        if not strweight(path):
            return
        if not path.endswith(f'.{f}'):
            path += '.' + f
        if f == 'xlsx':
            self.df.to_excel(path, index=False)
        elif f == 'csv':
            self.df.to_csv(path, index=False)
        elif f == 'sqlite':
            conn = sqlite3.connect(path)
            self.df.to_sql(name='standard', con=conn, index=False)
            conn.close()

    def get_focused(self):
        return self.columns.currentRow()

    def paint_current(self, color):
        self.columns.currentItem().setBackground(color)

    def on_toggle_target(self):
        idx = self.get_focused()
        self.states[idx] = not self.states[idx]
        self.paint_current(QtGui.QColor(TARGET_COLOR)
            if self.states[idx] else QtGui.QColor.fromRgba64(0, 0, 0, 0))

    def analyse(self):
        col = self.df.columns[self.get_focused()]
        self.analysis_win = QtWidgets.QMainWindow()
        self.analysis_win_ui = AnalysisCenter(self.df, col, self.states, self.types)
        self.analysis_win_ui.setupUi(self.analysis_win)
        self.analysis_win.show()

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Анализ данных"))
        self.save.setText(_translate("MainWindow", "Сохранить"))
        self.label.setText(_translate("MainWindow", "Сохранить в другом формате"))
        self.label_2.setText(_translate("MainWindow", "Операции с колонками"))
        self.make_analysis.setText(_translate("MainWindow", "Провести анализ"))
        self.toggle_target.setText(_translate("MainWindow", "Сменить статус"))
        self.label_3.setText(_translate("MainWindow", f'База данных "{self.df_name}"'))
        self.label_4.setText(_translate("MainWindow", "Целевые переменные помечены цветом."))
        self.reload.setText(_translate("MainWindow", "Открыть другую БД"))
    
    def make_label(self, name, status):
        label = ' ' * MIN_GAP + f'[{status}]'
        r = LABEL_LEN - len(label) - MIN_GAP
        if r < len(name):
            label = name[:r - 3] + '...' + label
        else:
            label = name + ' ' * (r - len(name)) + label
        return label

    def add_column(self, name, status):
        label = self.make_label(name, status)
        item = QtWidgets.QListWidgetItem(label)
        self.columns.addItem(item)



if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = BodyWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
