import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QWidget, QFileDialog, QPlainTextEdit, QLabel
from PyQt5.QtCore import Qt
from typing import List
import re

from parsercsv import *

class Transaction:
    def __init__(self, amount: float, date: date, memo: str, description: str, category: str, tag: str):
        self.amount = amount
        self.date = date
        self.memo = memo
        self.description = description
        self.category = category
        self.tag = tag

    def __str__(self):
        return f"Transaction: \nAmount: {self.amount}\nDescription: {self.description}\nCategory: {self.category}\nDate: {self.date}\nMemo: {self.memo}\nTag: {self.tag}"

class TransactionApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Transaction Manager")
        self.setGeometry(100, 100, 800, 600)

        # Create a central widget and layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create a QTextEdit widget to add memo filters
        self.memo_filter_textbox = QPlainTextEdit(self)
        self.memo_filter_textbox.setFixedHeight(50)
        self.memo_filter_textbox.setPlainText("ONLINE TRANSFER .*\nONLINE PAYMENT THANK YOU")
        layout.addWidget(self.memo_filter_textbox)

        # Create a table to display transactions
        self.table = QTableWidget(self)
        layout.addWidget(self.table)

        # Create total display
        self.total_label = QLabel(self)
        self.total_label.setText("$0.00")
        layout.addWidget(self.total_label)

        # Create buttons
        load_button = QPushButton("Load Transactions", self)
        load_button.clicked.connect(self.load_transactions)
        layout.addWidget(load_button)

        save_button = QPushButton("Save to CSV", self)
        save_button.clicked.connect(self.save_to_csv)
        layout.addWidget(save_button)

        # Member variable to store transactions
        self.transactions: List[Transaction] = []

        self.memo_filter_textbox.textChanged.connect(self.display_transactions)

    def memo_filter (self, transaction) -> List[str]:
        filters = self.memo_filter_textbox.toPlainText().split("\n")
        for f in filters:
            if re.match(f, transaction.memo):
                return False
        return True
    
    def get_filtered_transactions(self):
        return list(filter(self.memo_filter, self.transactions))
                    
    def load_transactions(self):
        directory_path = QFileDialog.getExistingDirectory(self, "Select Directory", "")
        if directory_path:
            default_category = ""
            default_tag = ""
            self.transactions = parse_transactions_from_directory(directory_path, default_category, default_tag)
            self.display_transactions()

    def display_transactions(self):
        self.table.setRowCount(len(self.get_filtered_transactions()))
        self.table.setColumnCount(6)
        headers = ["Date", "Amount", "Category", "Tag", "Description", "Memo"]
        self.table.setHorizontalHeaderLabels(headers)

        for row, transaction in enumerate(self.get_filtered_transactions()):
            date_item = QTableWidgetItem(transaction.date.strftime('%m/%d/%Y'))
            date_item.setFlags(date_item.flags() ^ Qt.ItemIsEditable)
            self.table.setItem(row, 0, date_item)
            
            amount_item = QTableWidgetItem(f"${transaction.amount:.2f}")
            amount_item.setFlags(amount_item.flags() ^ Qt.ItemIsEditable)
            self.table.setItem(row, 1, amount_item)

            self.table.setItem(row, 2, QTableWidgetItem(transaction.category))

            self.table.setItem(row, 3, QTableWidgetItem(transaction.tag))

            self.table.setItem(row, 4, QTableWidgetItem(transaction.description))

            memo_item = QTableWidgetItem(transaction.memo)
            date_item.setFlags(memo_item.flags() ^ Qt.ItemIsEditable)
            self.table.setItem(row, 5, memo_item)

        # Connect signals for category and tag changes
        self.table.itemChanged.connect(self.handle_item_change)
        self.total_label.setText(f"${sum_transaction_amounts(self.get_filtered_transactions()):.2f}")

    def handle_item_change(self, item):
        row = item.row()
        col = item.column()

        if col == 2:  # Category column
            self.get_filtered_transactions()[row].category = item.text()
        elif col == 3:  # Tag column
            self.get_filtered_transactions()[row].tag = item.text()
        elif col == 4:  # Description column
            self.get_filtered_transactions()[row].description = item.text()

    def save_to_csv(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save CSV", "", "Comma Separated Values (*.csv)")
        if file_path:
            write_transactions_to_csv(self.get_filtered_transactions(), file_path)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TransactionApp()
    window.show()
    sys.exit(app.exec_())
