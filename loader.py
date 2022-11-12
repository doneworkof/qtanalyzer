from PyQt5 import QtCore, QtGui, QtWidgets
import pandas as pd
import os
import sqlite3
from body import BodyWindow
import sys
from tools import strweight


def sql_to_pandas(path, table):
    conn = sqlite3.connect(path)
    df = pd.read_sql_query(f'SELECT * FROM {table}', conn)
    conn.close()
    return df


def get_table_names_of_sql(path):
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute('select name from sqlite_master where type="table"')
    tables = [c[0] for c in cur.fetchall()]
    return tables[1:]

class Ui_MainWindow(object):
    def __init__(self):
        super(Ui_MainWindow, self).__init__()
        self.last_path = ''
        self.format = ''

    def setupUi(self, MainWindow):
        self.win = MainWindow
        MainWindow.setObjectName("MainWindow")
        MainWindow.setFixedSize(381, 243)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(10, 10, 361, 221))
        self.tabWidget.setTabPosition(QtWidgets.QTabWidget.North)
        self.tabWidget.setTabsClosable(False)
        self.tabWidget.setTabBarAutoHide(False)
        self.tabWidget.setObjectName("tabWidget")
        self.tab1 = QtWidgets.QWidget()
        self.tab1.setObjectName("tab1")
        self.label = QtWidgets.QLabel(self.tab1)
        self.label.setGeometry(QtCore.QRect(20, 10, 311, 31))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.entry1 = QtWidgets.QLineEdit(self.tab1)
        self.entry1.setGeometry(QtCore.QRect(20, 80, 251, 21))
        self.entry1.setObjectName("entry1")
        self.browse = QtWidgets.QPushButton(self.tab1)
        self.browse.setGeometry(QtCore.QRect(275, 80, 65, 23))
        self.browse.setObjectName("browse")
        self.browse.clicked.connect(self.on_browse)
        self.error1 = QtWidgets.QLabel(self.tab1)
        self.error1.setGeometry(QtCore.QRect(20, 160, 181, 20))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
        self.error1.setPalette(palette)
        self.error1.setWordWrap(False)
        self.error1.setObjectName("error1")
        self.label_2 = QtWidgets.QLabel(self.tab1)
        self.label_2.setGeometry(QtCore.QRect(20, 50, 221, 20))
        self.label_2.setWordWrap(False)
        self.label_2.setObjectName("label_2")
        self.confirm1 = QtWidgets.QPushButton(self.tab1)
        self.confirm1.setGeometry(QtCore.QRect(210, 160, 121, 23))
        self.confirm1.setObjectName("confirm1")
        self.label_3 = QtWidgets.QLabel(self.tab1)
        self.label_3.setGeometry(QtCore.QRect(20, 110, 221, 16))
        self.label_3.setObjectName("label_3")
        self.tabWidget.addTab(self.tab1, "")
        self.tab2 = QtWidgets.QWidget()
        self.tab2.setObjectName("tab2")
        self.label_5 = QtWidgets.QLabel(self.tab2)
        self.label_5.setGeometry(QtCore.QRect(20, 10, 311, 31))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.label_5.setFont(font)
        self.label_5.setAlignment(QtCore.Qt.AlignCenter)
        self.label_5.setObjectName("label_5")
        self.label_6 = QtWidgets.QLabel(self.tab2)
        self.label_6.setGeometry(QtCore.QRect(20, 50, 321, 31))
        self.label_6.setWordWrap(True)
        self.label_6.setObjectName("label_6")
        self.choose_table = QtWidgets.QComboBox(self.tab2)
        self.choose_table.setGeometry(QtCore.QRect(20, 90, 311, 22))
        self.choose_table.setObjectName("choose_table")
        self.error2 = QtWidgets.QLabel(self.tab2)
        self.error2.setGeometry(QtCore.QRect(20, 120, 311, 20))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
        self.error2.setPalette(palette)
        self.error2.setWordWrap(False)
        self.error2.setObjectName("error2")
        self.confirm2 = QtWidgets.QPushButton(self.tab2)
        self.confirm2.setGeometry(QtCore.QRect(210, 160, 121, 23))
        self.confirm2.setObjectName("confirm2")
        self.cancel = QtWidgets.QPushButton(self.tab2)
        self.cancel.setGeometry(QtCore.QRect(20, 160, 121, 23))
        self.cancel.setObjectName("cancel")
        self.tabWidget.addTab(self.tab2, "")
        MainWindow.setCentralWidget(self.centralwidget)
        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        self.select_tab(0)
        self.confirm1.clicked.connect(self.on_confirmed1)
        self.cancel.clicked.connect(lambda: self.select_tab(0))
        self.confirm2.clicked.connect(self.on_confirmed2)
        self.entry1.setFocus(True)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Начало работы"))
        self.label.setText(_translate("MainWindow", "Загрузка базы данных"))
        self.error1.setText(_translate("MainWindow", ""))
        self.label_2.setText(_translate("MainWindow", "Введите путь к таблице для обработки:"))
        self.confirm1.setText(_translate("MainWindow", "Подтвердить"))
        self.label_3.setText(_translate("MainWindow", "*Допустимые форматы: XLSX, CSV, SQL, DB"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab1), _translate("MainWindow", "Открытие файла"))
        self.label_5.setText(_translate("MainWindow", "Дополнительные настройки"))
        self.label_6.setText(_translate("MainWindow", "Ваша база данных имеет формат SQLITE, поэтому необходимо ввести имя целевой таблицы внутри неё:"))
        self.error2.setText(_translate("MainWindow", ""))
        self.confirm2.setText(_translate("MainWindow", "Подтвердить"))
        self.cancel.setText(_translate("MainWindow", "Назад"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab2), _translate("MainWindow", "Дополнительно"))
        self.browse.setText(_translate("MainWindow", "Открыть"))

    def launch(self, df):
        self.body = QtWidgets.QMainWindow()
        self.body_ui = BodyWindow(df, self.last_path, self.format, Ui_MainWindow)
        self.body_ui.setupUi(self.body)
        self.body.show()
        self.win.close()
        
    def select_tab(self, idx):
        self.tabWidget.setTabEnabled(1 - idx, False)
        self.tabWidget.setTabEnabled(idx, True)
        self.tabWidget.setCurrentIndex(idx)
        if idx == 1:
            self.choose_table.setFocus(True)
        self.error('')
        self.error('', 1)

    def error(self, text, idx=0):
        [self.error1, self.error2][idx].setText(text)

    def on_confirmed2(self):
        try:
            table = self.choose_table.currentText()
            if not strweight(table):
                return self.error('Неверное название!', 1)
            df = sql_to_pandas(self.last_path, table)
            self.format = 'sqlite'
            self.launch(df)
        except Exception as ex:
            print(ex)
            self.error('Неизвестная ошибка!', 1)

    def on_browse(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            directory=os.getcwd()
        )
        if strweight(path):
            self.entry1.setText(path)

    def on_confirmed1(self):
        try:
            path = self.entry1.text()
            self.last_path = path
            if not strweight(path) or not os.path.exists(path):
                return self.error('Неверный путь!')
            elif path.endswith('.xlsx'):
                df = pd.read_excel(path)
                self.format = 'xlsx'
            elif path.endswith('.csv'):
                df = pd.read_csv(path)
                self.format = 'csv'
            elif path.endswith('.sqlite') or path.endswith('.db'):
                self.choose_table.clear()
                tables = get_table_names_of_sql(path)
                self.choose_table.addItems(tables)
                return self.select_tab(1)
            else:
                return self.error('Неверный формат!')
            self.launch(df)
        except Exception as ex:
            raise ex
            print(ex)
            self.error('Неизвестная ошибка!')


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
