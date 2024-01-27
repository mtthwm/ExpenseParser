import csv
import sqlite3
from datetime import date, datetime
from typing import List
import os

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

def parse_csv(file_path: str, default_category: str, default_tag: str) -> List[Transaction]:
    transactions: List[Transaction] = []

    with open(file_path, newline='') as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=',')

        for row in csv_reader:
            # Extract relevant information from the CSV row
            date_str, amount_str, _, _, memo = row
            amount = -float(amount_str)

            # Convert date string to datetime object
            date = datetime.strptime(date_str, '%m/%d/%Y').date()

            # Create a Transaction instance and append it to the list
            transaction = Transaction(amount, date, memo, "", default_category, default_tag)
            transactions.append(transaction)

    return transactions

def write_transactions_to_csv(transactions: List[Transaction], file_path: str) -> None:
    with open(file_path, 'w', newline='') as csvfile:
        fieldnames = ['Date', 'Amount', 'Category', 'Tag', 'Description', 'Memo']
        csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        csv_writer.writeheader()

        for transaction in transactions:
            csv_writer.writerow({
                'Date': transaction.date.strftime('%m/%d/%Y'),
                'Amount': f"${transaction.amount:.2f}",
                'Category': transaction.category,
                'Tag': transaction.tag,
                'Description': transaction.description,
                'Memo': transaction.memo
            })

def sum_transaction_amounts(transactions: List[Transaction]) -> float:
    return sum(transaction.amount for transaction in transactions)

def find_csv_files_in_directory(directory_path: str) -> List[str]:
    csv_files: List[str] = []

    for file_name in os.listdir(directory_path):
        if file_name.endswith('.csv'):
            file_path = os.path.join(directory_path, file_name)
            csv_files.append(file_path)

    return csv_files

def parse_transactions_from_directory(directory_path: str, default_category: str, default_tag: str) -> List[Transaction]:
    transactions: List[Transaction] = []

    # Find CSV files in the directory
    csv_files = find_csv_files_in_directory(directory_path)

    # Parse transactions from each CSV file
    for csv_file in csv_files:
        parsed_transactions = parse_csv(csv_file, default_category, default_tag)
        transactions.extend(parsed_transactions)

        # Delete the CSV file after parsing
        # os.remove(csv_file)

    return transactions

def create_transactions_database_schema(database_path: str) -> None:
    # Connect to the SQLite database
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Create the Transactions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Transactions (
            id INTEGER PRIMARY KEY,
            amount REAL NOT NULL,
            date TEXT NOT NULL,
            memo TEXT,
            description TEXT,
            category TEXT,
            tag TEXT
        )
    ''')

    # Commit changes and close the connection
    conn.commit()
    conn.close()

def add_transactions_to_database(transactions: List[Transaction], database_path: str) -> None:
    # Connect to the SQLite database
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Insert transactions into the Transactions table
    for transaction in transactions:
        cursor.execute('''
            INSERT INTO Transactions (amount, date, memo, description, category, tag)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (transaction.amount, transaction.date, transaction.memo, transaction.description, transaction.category, transaction.tag))

    # Commit changes and close the connection
    conn.commit()
    conn.close()

def get_transactions_from_database(database_path: str, query: str) -> List[Transaction]:
    # Connect to the SQLite database
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Execute the query and fetch transactions
    cursor.execute(query)
    rows = cursor.fetchall()

    # Create a list of Transaction instances from the fetched rows
    transactions: List[Transaction] = []
    for row in rows:
        amount, date_str, memo, description, category_text, tag_text = row
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        amount = float(amount)
        category = category_text
        tag = tag_text

        transaction = Transaction(amount, date, memo, description, category, tag)
        transactions.append(transaction)

    # Close the connection
    conn.close()

    return transactions