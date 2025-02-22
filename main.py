import sys
import sqlite3
from PyQt6 import QtWidgets, uic


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)
        self.conn = sqlite3.connect('coffee.sqlite')
        self.init_db()
        self.load_data()
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
                price REAL,
                volume INTEGER
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
        coffee_id = self.tableWidget.item(selected_row, 0).text()
        dialog = AddEditCoffeeForm(coffee_id=int(coffee_id))
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            self.load_data()

    def closeEvent(self, event):
        self.conn.close()


class AddEditCoffeeForm(QtWidgets.QDialog):
    def __init__(self, coffee_id=None):
        super().__init__()
        uic.loadUi('addEditCoffeeForm.ui', self)

        self.coffee_id = coffee_id
        self.conn = sqlite3.connect('coffee.sqlite')

        # Подключаем сигналы QDialogButtonBox
        self.buttonBox.accepted.connect(self.save_coffee)
        self.buttonBox.rejected.connect(self.reject)

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
            index = self.roastLevelCombo.findText(data[1])
            if index != -1:
                self.roastLevelCombo.setCurrentIndex(index)
            index = self.typeCombo.findText(data[2])
            if index != -1:
                self.typeCombo.setCurrentIndex(index)
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
