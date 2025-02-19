# main.py
import sys
import sqlite3
from PyQt6 import QtWidgets
from UI.main_ui import Ui_MainWindow
from UI.add_edit_ui import Ui_AddEditCoffeeForm

class CoffeeApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.load_data()
        self.editButton.clicked.connect(self.open_edit_form)

    def load_data(self):
        conn = sqlite3.connect('data/coffee.sqlite')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM coffee")
        data = cursor.fetchall()
        self.tableWidget.setRowCount(len(data))
        for i, row in enumerate(data):
            for j, value in enumerate(row):
                self.tableWidget.setItem(i, j, QtWidgets.QTableWidgetItem(str(value)))
        conn.close()

    def open_edit_form(self):
        self.edit_form = AddEditCoffeeForm()
        self.edit_form.show()

class AddEditCoffeeForm(QtWidgets.QDialog, Ui_AddEditCoffeeForm):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.saveButton.clicked.connect(self.save_data)

    def save_data(self):
        conn = sqlite3.connect('data/coffee.sqlite')
        cursor = conn.cursor()

        values = [le.text() for le in self.lineEdits]
        if values[0]:  # Если указан ID, обновляем запись
            cursor.execute("""
                UPDATE coffee
                SET name=?, roast=?, form=?, description=?, price=?, volume=?
                WHERE id=?
            """, values[1:] + [values[0]])
        else:  # Иначе добавляем новую запись
            cursor.execute("""
                INSERT INTO coffee (name, roast, form, description, price, volume)
                VALUES (?, ?, ?, ?, ?, ?)
            """, values[1:])
        conn.commit()
        conn.close()
        self.close()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = CoffeeApp()
    window.show()
    sys.exit(app.exec())
