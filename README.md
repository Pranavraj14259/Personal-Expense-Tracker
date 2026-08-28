# Personal Expense Tracker

A Python-based desktop application for managing personal income, expenses, monthly and yearly financial records, reports, multiple currencies, transaction search, sorting, CSV export, and database backup.

## Features
- Add transactions
- View transactions
- Search and sort transactions
- Multiple currencies
- Monthly and yearly reports
- Export data
- Database backup

### Transaction Management
- Add new income and expense transactions
- View all transactions
- Search transactions by ID
- Update existing transactions
- Delete one transaction
- Delete all transactions
- Transaction IDs restart from 1 after deleting all transactions

### Amount and Currency Support
- Supports multiple currencies
- Indian Rupee (INR)
- US Dollar (USD)
- Euro (EUR)
- British Pound (GBP)
- Japanese Yen (JPY)
- Chinese Yuan (CNY)
- Australian Dollar (AUD)
- Canadian Dollar (CAD)
- Singapore Dollar (SGD)
- UAE Dirham (AED)
- Saudi Riyal (SAR)
- Swiss Franc (CHF)
- Custom/Other currency option

### Number Formatting
The application accepts both Indian and American comma formatting.

Examples:

- `1,00,000.69`
- `100,000.69`
- `100000.69`

Decimal values and paisa/cents are supported.

### Advanced Search
The advanced search feature allows filtering transactions by:

- Transaction ID
- Description
- Category
- Currency
- Type
- Date

Transactions can also be sorted by:

- ID
- Date
- Description
- Category
- Amount
- Currency
- Type

Sorting supports:

- Ascending
- Descending

### Financial Reports
- Financial summary
- Financial dashboard
- Monthly report
- Category-wise report
- Monthly income
- Monthly expenses
- Yearly income
- Yearly expenses
- Monthly savings
- Yearly savings
- Yearly comparison

### Monthly and Yearly Records
You can separately record:

- Monthly income
- Monthly expenses
- Yearly income
- Yearly expenses

The application calculates the corresponding savings and yearly totals.

### Export and Backup
- Export transactions to CSV
- Export monthly/yearly records to CSV
- Backup the SQLite database

### User Interface
- Resizable application window
- Maximizable application window
- Scrollable interface
- Mouse-wheel scrolling
- Separate windows for different operations

## Technologies Used

- Python
- Tkinter
- SQLite
- CSV
- Object-Oriented Programming

## Project Structure

```text
Personal-Expense-Tracker/
│
├── main.py
├── gui.py
├── transaction.py
├── database.py
├── README.md
├── LICENSE
└── .gitignore
