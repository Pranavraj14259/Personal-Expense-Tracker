import sqlite3


DATABASE_NAME = "expenses.db"


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    return sqlite3.connect(DATABASE_NAME)


# ============================================================
# CREATE DATABASE TABLES
# ============================================================

def create_table():
    connection = get_connection()
    cursor = connection.cursor()

    # --------------------------------------------------------
    # NORMAL TRANSACTIONS
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            currency TEXT NOT NULL DEFAULT 'INR',
            transaction_type TEXT NOT NULL,
            payment_method TEXT NOT NULL
        )
    """)

    transaction_columns = {
        row[1]
        for row in cursor.execute(
            "PRAGMA table_info(transactions)"
        ).fetchall()
    }

    if "currency" not in transaction_columns:
        cursor.execute("""
            ALTER TABLE transactions
            ADD COLUMN currency TEXT NOT NULL DEFAULT 'INR'
        """)

    # --------------------------------------------------------
    # RECURRING RECORDS
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recurring_records (
            record_id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            currency TEXT NOT NULL DEFAULT 'INR',
            record_type TEXT NOT NULL,
            frequency TEXT NOT NULL,
            start_year INTEGER NOT NULL
        )
    """)

    connection.commit()
    connection.close()


def initialize_database():
    create_table()


# ============================================================
# NORMAL TRANSACTIONS
# ============================================================

def add_transaction(transaction):
    initialize_database()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO transactions (
            date,
            description,
            category,
            amount,
            currency,
            transaction_type,
            payment_method
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        transaction["date"],
        transaction["description"],
        transaction["category"],
        transaction["amount"],
        transaction["currency"],
        transaction["transaction_type"],
        transaction["payment_method"]
    ))

    connection.commit()
    connection.close()


def get_all_transactions():
    initialize_database()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            transaction_id,
            date,
            description,
            category,
            amount,
            currency,
            transaction_type,
            payment_method
        FROM transactions
        ORDER BY transaction_id DESC
    """)

    rows = cursor.fetchall()

    connection.close()

    transactions = []

    for row in rows:
        transactions.append({
            "transaction_id": row[0],
            "date": row[1],
            "description": row[2],
            "category": row[3],
            "amount": row[4],
            "currency": row[5],
            "transaction_type": row[6],
            "payment_method": row[7]
        })

    return transactions


def find_transaction(transaction_id):
    initialize_database()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            transaction_id,
            date,
            description,
            category,
            amount,
            currency,
            transaction_type,
            payment_method
        FROM transactions
        WHERE transaction_id = ?
    """, (transaction_id,))

    row = cursor.fetchone()

    connection.close()

    if row is None:
        return None

    return {
        "transaction_id": row[0],
        "date": row[1],
        "description": row[2],
        "category": row[3],
        "amount": row[4],
        "currency": row[5],
        "transaction_type": row[6],
        "payment_method": row[7]
    }


def update_transaction(transaction):
    initialize_database()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE transactions
        SET
            date = ?,
            description = ?,
            category = ?,
            amount = ?,
            currency = ?,
            transaction_type = ?,
            payment_method = ?
        WHERE transaction_id = ?
    """, (
        transaction["date"],
        transaction["description"],
        transaction["category"],
        transaction["amount"],
        transaction["currency"],
        transaction["transaction_type"],
        transaction["payment_method"],
        transaction["transaction_id"]
    ))

    updated = cursor.rowcount

    connection.commit()
    connection.close()

    return updated > 0


def delete_transaction(transaction_id):
    initialize_database()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM transactions WHERE transaction_id = ?",
        (transaction_id,)
    )

    deleted = cursor.rowcount

    connection.commit()
    connection.close()

    return deleted > 0


def delete_all_transactions():
    initialize_database()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM transactions"
    )

    total = cursor.fetchone()[0]

    cursor.execute(
        "DELETE FROM transactions"
    )

    # Reset AUTO_INCREMENT
    cursor.execute("""
        DELETE FROM sqlite_sequence
        WHERE name = 'transactions'
    """)

    connection.commit()
    connection.close()

    return total


# ============================================================
# FINANCIAL SUMMARY
# ============================================================

def get_summary():
    initialize_database()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            currency,

            COALESCE(
                SUM(
                    CASE
                        WHEN transaction_type = 'Income'
                        THEN amount
                        ELSE 0
                    END
                ),
                0
            ),

            COALESCE(
                SUM(
                    CASE
                        WHEN transaction_type = 'Expense'
                        THEN amount
                        ELSE 0
                    END
                ),
                0
            )

        FROM transactions

        GROUP BY currency

        ORDER BY currency
    """)

    rows = cursor.fetchall()

    connection.close()

    summaries = []

    for row in rows:
        summaries.append({
            "currency": row[0],
            "income": row[1],
            "expenses": row[2],
            "balance": row[1] - row[2]
        })

    return summaries


# ============================================================
# MONTHLY REPORT
# ============================================================

def get_monthly_summary(month, year):
    initialize_database()

    connection = get_connection()
    cursor = connection.cursor()

    month_pattern = f"{month:02d}-%-{year}"

    cursor.execute("""
        SELECT
            currency,

            COALESCE(
                SUM(
                    CASE
                        WHEN transaction_type = 'Income'
                        THEN amount
                        ELSE 0
                    END
                ),
                0
            ),

            COALESCE(
                SUM(
                    CASE
                        WHEN transaction_type = 'Expense'
                        THEN amount
                        ELSE 0
                    END
                ),
                0
            ),

            COUNT(*)

        FROM transactions

        WHERE date LIKE ?

        GROUP BY currency

        ORDER BY currency
    """, (month_pattern,))

    rows = cursor.fetchall()

    connection.close()

    reports = []

    for row in rows:
        reports.append({
            "currency": row[0],
            "income": row[1],
            "expenses": row[2],
            "balance": row[1] - row[2],
            "transactions": row[3]
        })

    return reports


# ============================================================
# CATEGORY REPORT
# ============================================================

def get_category_summary():
    initialize_database()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            currency,
            category,
            COALESCE(SUM(amount), 0),
            COUNT(*)

        FROM transactions

        WHERE transaction_type = 'Expense'

        GROUP BY currency, category

        ORDER BY currency, SUM(amount) DESC
    """)

    rows = cursor.fetchall()

    connection.close()

    categories = []

    for row in rows:
        categories.append({
            "currency": row[0],
            "category": row[1],
            "amount": row[2],
            "transactions": row[3]
        })

    return categories


# ============================================================
# RECURRING RECORDS
# ============================================================

def add_recurring_record(record):
    initialize_database()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO recurring_records (
            description,
            category,
            amount,
            currency,
            record_type,
            frequency,
            start_year
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        record["description"],
        record["category"],
        record["amount"],
        record["currency"],
        record["record_type"],
        record["frequency"],
        record["start_year"]
    ))

    connection.commit()
    connection.close()


def get_recurring_records():
    initialize_database()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            record_id,
            description,
            category,
            amount,
            currency,
            record_type,
            frequency,
            start_year
        FROM recurring_records
        ORDER BY record_id DESC
    """)

    rows = cursor.fetchall()

    connection.close()

    records = []

    for row in rows:
        records.append({
            "record_id": row[0],
            "description": row[1],
            "category": row[2],
            "amount": row[3],
            "currency": row[4],
            "record_type": row[5],
            "frequency": row[6],
            "start_year": row[7]
        })

    return records


def update_recurring_record(record):
    initialize_database()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE recurring_records
        SET
            description = ?,
            category = ?,
            amount = ?,
            currency = ?,
            record_type = ?,
            frequency = ?,
            start_year = ?
        WHERE record_id = ?
    """, (
        record["description"],
        record["category"],
        record["amount"],
        record["currency"],
        record["record_type"],
        record["frequency"],
        record["start_year"],
        record["record_id"]
    ))

    updated = cursor.rowcount

    connection.commit()
    connection.close()

    return updated > 0


def delete_recurring_record(record_id):
    initialize_database()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM recurring_records WHERE record_id = ?",
        (record_id,)
    )

    deleted = cursor.rowcount

    connection.commit()
    connection.close()

    return deleted > 0


def delete_all_recurring_records():
    initialize_database()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM recurring_records"
    )

    total = cursor.fetchone()[0]

    cursor.execute(
        "DELETE FROM recurring_records"
    )

    cursor.execute("""
        DELETE FROM sqlite_sequence
        WHERE name = 'recurring_records'
    """)

    connection.commit()
    connection.close()

    return total


# ============================================================
# RECURRING SUMMARY
# ============================================================

def get_recurring_summary():
    initialize_database()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            currency,
            record_type,
            frequency,
            COALESCE(SUM(amount), 0)

        FROM recurring_records

        GROUP BY currency, record_type, frequency

        ORDER BY currency, frequency, record_type
    """)

    rows = cursor.fetchall()

    connection.close()

    return rows


def get_recurring_year_summary(year):
    initialize_database()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            currency,

            COALESCE(
                SUM(
                    CASE
                        WHEN record_type = 'Income'
                        AND frequency = 'Monthly'
                        THEN amount * 12

                        WHEN record_type = 'Income'
                        AND frequency = 'Yearly'
                        THEN amount

                        ELSE 0
                    END
                ),
                0
            ),

            COALESCE(
                SUM(
                    CASE
                        WHEN record_type = 'Expense'
                        AND frequency = 'Monthly'
                        THEN amount * 12

                        WHEN record_type = 'Expense'
                        AND frequency = 'Yearly'
                        THEN amount

                        ELSE 0
                    END
                ),
                0
            )

        FROM recurring_records

        WHERE start_year = ?

        GROUP BY currency

        ORDER BY currency
    """, (year,))

    rows = cursor.fetchall()

    connection.close()

    results = []

    for row in rows:
        results.append({
            "currency": row[0],
            "income": row[1],
            "expenses": row[2],
            "savings": row[1] - row[2]
        })

    return results


# ============================================================
# YEARLY COMPARISON
# ============================================================

def get_yearly_comparison(year1, year2):

    first_year = get_recurring_year_summary(year1)
    second_year = get_recurring_year_summary(year2)

    first_dict = {
        item["currency"]: item
        for item in first_year
    }

    second_dict = {
        item["currency"]: item
        for item in second_year
    }

    currencies = (
        set(first_dict.keys())
        |
        set(second_dict.keys())
    )

    results = []

    for currency in sorted(currencies):

        first = first_dict.get(
            currency,
            {
                "income": 0,
                "expenses": 0,
                "savings": 0
            }
        )

        second = second_dict.get(
            currency,
            {
                "income": 0,
                "expenses": 0,
                "savings": 0
            }
        )

        income_change = (
            second["income"]
            -
            first["income"]
        )

        expense_change = (
            second["expenses"]
            -
            first["expenses"]
        )

        savings_change = (
            second["savings"]
            -
            first["savings"]
        )

        if first["income"] != 0:
            income_percentage = (
                income_change
                /
                abs(first["income"])
            ) * 100
        else:
            income_percentage = 0

        if first["expenses"] != 0:
            expense_percentage = (
                expense_change
                /
                abs(first["expenses"])
            ) * 100
        else:
            expense_percentage = 0

        if first["savings"] != 0:
            savings_percentage = (
                savings_change
                /
                abs(first["savings"])
            ) * 100
        else:
            savings_percentage = 0

        results.append({
            "currency": currency,

            "year1_income": first["income"],
            "year2_income": second["income"],
            "income_change": income_change,
            "income_percentage": income_percentage,

            "year1_expenses": first["expenses"],
            "year2_expenses": second["expenses"],
            "expense_change": expense_change,
            "expense_percentage": expense_percentage,

            "year1_savings": first["savings"],
            "year2_savings": second["savings"],
            "savings_change": savings_change,
            "savings_percentage": savings_percentage
        })

    return results


# ============================================================
# EXPORT NORMAL TRANSACTIONS
# ============================================================

def export_transactions_data():
    initialize_database()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            transaction_id,
            date,
            description,
            category,
            amount,
            currency,
            transaction_type,
            payment_method
        FROM transactions
        ORDER BY transaction_id
    """)

    rows = cursor.fetchall()

    connection.close()

    return rows


# ============================================================
# EXPORT RECURRING RECORDS
# ============================================================

def export_recurring_data():
    initialize_database()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            record_id,
            description,
            category,
            amount,
            currency,
            record_type,
            frequency,
            start_year
        FROM recurring_records
        ORDER BY record_id
    """)

    rows = cursor.fetchall()

    connection.close()

    return rows