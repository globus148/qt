import sys
import sqlite3
from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QMessageBox


class AddEditCoffeeForm(QtWidgets.QDialog):
    def __init__(self, coffee_id=None):
        super().__init__()
        uic.loadUi('addEditCoffeeForm.ui', self)
        self.coffee_id = coffee_id
        self.saveButton.clicked.connect(self.save_data)

        if self.coffee_id:  # Если редактируем
            self.load_data()

    def load_data(self):
        connection = sqlite3.connect('coffee.sqlite')
        cursor = connection.cursor()
        cursor.execute('SELECT name, roast, ground_or_beans, taste, price, volume FROM coffee WHERE id=?',
                       (self.coffee_id,))
        data = cursor.fetchone()
        connection.close()

        if data:
            self.nameEdit.setText(data[0])
            self.roastEdit.setText(data[1])
            self.typeEdit.setText(data[2])
            self.tasteEdit.setText(data[3])
            self.priceEdit.setText(str(data[4]))
            self.volumeEdit.setText(str(data[5]))

    def save_data(self):
        name = self.nameEdit.text()
        roast = self.roastEdit.text()
        coffee_type = self.typeEdit.text()
        taste = self.tasteEdit.text()
        price = self.priceEdit.text()
        volume = self.volumeEdit.text()

        if not all([name, roast, coffee_type, price, volume]):
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, заполните все поля.")
            return

        connection = sqlite3.connect('coffee.sqlite')
        cursor = connection.cursor()

        if self.coffee_id:  # Редактирование
            cursor.execute('''
                UPDATE coffee SET name=?, roast=?, ground_or_beans=?, taste=?, price=?, volume=? WHERE id=?
            ''', (name, roast, coffee_type, taste, price, volume, self.coffee_id))
        else:  # Добавление
            cursor.execute('''
                INSERT INTO coffee (name, roast, ground_or_beans, taste, price, volume) VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, roast, coffee_type, taste, price, volume))

        connection.commit()
        connection.close()
        self.accept()


class CoffeeApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)
        self.addButton.clicked.connect(self.add_record)
        self.editButton.clicked.connect(self.edit_record)
        self.load_data()

    def load_data(self):
        connection = sqlite3.connect('coffee.sqlite')
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM coffee')
        records = cursor.fetchall()
        connection.close()

        self.tableWidget.setRowCount(len(records))
        self.tableWidget.setColumnCount(7)
        self.tableWidget.setHorizontalHeaderLabels(['ID', 'Название', 'Обжарка', 'Тип', 'Вкус', 'Цена', 'Объем'])

        for row_idx, row_data in enumerate(records):
            for col_idx, col_data in enumerate(row_data):
                self.tableWidget.setItem(row_idx, col_idx, QtWidgets.QTableWidgetItem(str(col_data)))

    def add_record(self):
        form = AddEditCoffeeForm()
        if form.exec_():
            self.load_data()

    def edit_record(self):
        selected_items = self.tableWidget.selectedItems()
        if selected_items:
            coffee_id = int(selected_items[0].text())
            form = AddEditCoffeeForm(coffee_id)
            if form.exec_():
                self.load_data()
        else:
            QMessageBox.warning(self, "Выбор записи", "Выберите запись для редактирования.")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = CoffeeApp()
    window.show()
    sys.exit(app.exec())
