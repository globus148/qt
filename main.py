import sys
import sqlite3
import os
from PyQt6 import QtWidgets
from UI.main_ui import Ui_MainWindow
from UI.add_edit_coffee_ui import Ui_Dialog
from PyQt6.QtCore import Qt


def get_db_path():
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_path, 'release/data', 'coffee.sqlite')
    return db_path


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Подключение к базе данных
        db_path = get_db_path()
        self.conn = sqlite3.connect(db_path)

        self.init_db()
        self.load_data()

        # Привязка кнопок
        self.addButton.clicked.connect(self.add_coffee)
        self.editButton.clicked.connect(self.edit_coffee)

    def init_db(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS coffee (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                roast_level TEXT,
                type TEXT,
                description TEXT,
                price REAL CHECK(price > 0),
                volume INTEGER CHECK(volume > 0)
            )
        ''')
        self.conn.commit()

    def load_data(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM coffee')
        results = cursor.fetchall()

        self.tableWidget.setRowCount(len(results))
        self.tableWidget.setColumnCount(7)
        self.tableWidget.setHorizontalHeaderLabels([
            'ID', 'Название', 'Обжарка', 'Тип', 'Описание', 'Цена', 'Объем'
        ])
        self.tableWidget.hideColumn(0)

        for row_idx, row_data in enumerate(results):
            for col_idx, col_data in enumerate(row_data):
                item = QtWidgets.QTableWidgetItem(str(col_data))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.tableWidget.setItem(row_idx, col_idx, item)

    def add_coffee(self):
        dialog = AddEditCoffeeForm()
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            self.load_data()

    def edit_coffee(self):
        selected_row = self.tableWidget.currentRow()
        if selected_row == -1:
            QtWidgets.QMessageBox.warning(self, 'Ошибка', 'Выберите запись для редактирования')
            return
        coffee_id = int(self.tableWidget.item(selected_row, 0).text())
        dialog = AddEditCoffeeForm(coffee_id=coffee_id)
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            self.load_data()

    def closeEvent(self, event):
        self.conn.close()
        event.accept()


class AddEditCoffeeForm(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self, coffee_id=None):
        super().__init__()
        self.setupUi(self)
        self.coffee_id = coffee_id
        self.conn = sqlite3.connect(get_db_path())

        # Привязка кнопок
        self.buttonBox.accepted.connect(self.save_coffee)
        self.buttonBox.rejected.connect(self.reject)

        # Заполнение ComboBox
        self.roastLevelCombo.addItems(['Light', 'Medium', 'Dark'])
        self.typeCombo.addItems(['Молотый', 'В зернах'])

        if self.coffee_id is not None:
            self.load_data()

    def load_data(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT name, roast_level, type, description, price, volume
            FROM coffee WHERE id = ?
        ''', (self.coffee_id,))
        data = cursor.fetchone()

        if data:
            self.nameEdit.setText(data[0])
            self.roastLevelCombo.setCurrentText(data[1])
            self.typeCombo.setCurrentText(data[2])
            self.descriptionEdit.setPlainText(data[3])
            self.priceSpin.setValue(data[4])
            self.volumeSpin.setValue(data[5])

    def save_coffee(self):
        name = self.nameEdit.text().strip()
        roast_level = self.roastLevelCombo.currentText()
        coffee_type = self.typeCombo.currentText()
        description = self.descriptionEdit.toPlainText().strip()
        price = self.priceSpin.value()
        volume = self.volumeSpin.value()

        if not name:
            QtWidgets.QMessageBox.warning(self, 'Ошибка', 'Введите название сорта')
            return
        if price <= 0:
            QtWidgets.QMessageBox.warning(self, 'Ошибка', 'Цена должна быть больше нуля')
            return
        if volume <= 0:
            QtWidgets.QMessageBox.warning(self, 'Ошибка', 'Объем должен быть больше нуля')
            return

        cursor = self.conn.cursor()
        if self.coffee_id is None:
            cursor.execute('''
                INSERT INTO coffee (name, roast_level, type, description, price, volume)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, roast_level, coffee_type, description, price, volume))
        else:
            cursor.execute('''
                UPDATE coffee
                SET name=?, roast_level=?, type=?, description=?, price=?, volume=?
                WHERE id=?
            ''', (name, roast_level, coffee_type, description, price, volume, self.coffee_id))
        self.conn.commit()
        self.accept()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
