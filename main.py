import sys
import sqlite3
from PyQt6 import QtWidgets, uic


class CoffeeApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)
        self.pushButton.clicked.connect(self.load_data)
        self.load_data()

    def load_data(self):
        connection = sqlite3.connect('coffee.sqlite')
        cursor = connection.cursor()

        cursor.execute('SELECT * FROM coffee')
        records = cursor.fetchall()

        # Настройка таблицы
        self.tableWidget.setRowCount(len(records))
        self.tableWidget.setColumnCount(7)
        self.tableWidget.setHorizontalHeaderLabels(['ID', 'Название', 'Обжарка', 'Тип', 'Вкус', 'Цена', 'Объем'])

        for row_idx, row_data in enumerate(records):
            for col_idx, col_data in enumerate(row_data):
                self.tableWidget.setItem(row_idx, col_idx, QtWidgets.QTableWidgetItem(str(col_data)))

        connection.close()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = CoffeeApp()
    window.show()
    sys.exit(app.exec())
