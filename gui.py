import csv
import os
import shutil
from datetime import datetime

import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from transaction import Transaction, RecurringRecord

from database import (
    add_transaction,
    get_all_transactions,
    find_transaction,
    update_transaction,
    delete_transaction,
    delete_all_transactions,
    get_summary,
    get_monthly_summary,
    get_category_summary,

    add_recurring_record,
    get_recurring_records,
    update_recurring_record,
    delete_recurring_record,
    delete_all_recurring_records,
    get_recurring_summary,
    get_yearly_comparison,

    export_transactions_data,
    export_recurring_data
)


# ============================================================
# MAIN WINDOW
# ============================================================

root = tk.Tk()

root.title("Personal Expense Tracker")
root.geometry("1000x700")
root.minsize(700, 500)
root.resizable(True, True)


# ============================================================
# CURRENCIES
# ============================================================

CURRENCIES = {
    "INR - Indian Rupee": "₹",
    "USD - US Dollar": "$",
    "EUR - Euro": "€",
    "GBP - British Pound": "£",
    "JPY - Japanese Yen": "¥",
    "CNY - Chinese Yuan": "¥",
    "AUD - Australian Dollar": "A$",
    "CAD - Canadian Dollar": "C$",
    "SGD - Singapore Dollar": "S$",
    "AED - UAE Dirham": "د.إ",
    "SAR - Saudi Riyal": "﷼",
    "CHF - Swiss Franc": "CHF ",
    "Other": ""
}


# ============================================================
# AMOUNT PARSING
# ============================================================

def parse_amount(value):
    """
    Accepts:
        1000
        1000.69
        1,000.69
        1,00,000.69
        ₹1,00,000.69
        $1,000.69
    """

    value = str(value).strip()

    for symbol in [
        "₹",
        "$",
        "€",
        "£",
        "¥"
    ]:
        value = value.replace(symbol, "")

    value = value.replace(" ", "")

    if not value:
        raise ValueError(
            "Amount cannot be empty."
        )

    if value.count(".") > 1:
        raise ValueError(
            "Invalid amount format."
        )

    # This allows both Indian and American comma formatting.
    value = value.replace(",", "")

    try:
        amount = float(value)
    except ValueError:
        raise ValueError(
            "Enter a valid amount.\n\n"
            "Examples:\n"
            "1,00,000.69\n"
            "100,000.69\n"
            "100000.69"
        )

    if amount <= 0:
        raise ValueError(
            "Amount must be greater than 0."
        )

    return amount


# ============================================================
# CURRENCY FORMATTING
# ============================================================

def format_currency(amount, currency):

    if amount is None:
        amount = 0

    amount = float(amount)

    symbol = CURRENCIES.get(
        currency,
        ""
    )

    negative = amount < 0

    amount = abs(amount)

    integer_part, decimal_part = (
        f"{amount:.2f}".split(".")
    )

    # Indian number formatting
    if currency.startswith("INR"):

        if len(integer_part) <= 3:

            formatted_integer = integer_part

        else:

            last_three = integer_part[-3:]
            remaining = integer_part[:-3]

            groups = []

            while len(remaining) > 2:

                groups.insert(
                    0,
                    remaining[-2:]
                )

                remaining = remaining[:-2]

            if remaining:

                groups.insert(
                    0,
                    remaining
                )

            formatted_integer = (
                ",".join(groups)
                + ","
                + last_three
            )

    else:

        # American-style formatting for other currencies
        formatted_integer = (
            f"{int(integer_part):,}"
        )

    result = (
        f"{symbol}"
        f"{formatted_integer}."
        f"{decimal_part}"
    )

    if negative:
        result = "-" + result

    return result


# ============================================================
# DATE VALIDATION
# ============================================================

def validate_date(date_text):

    date_text = str(
        date_text
    ).strip()

    try:

        return datetime.strptime(
            date_text,
            "%d-%m-%Y"
        )

    except ValueError:

        raise ValueError(
            "Enter a valid date in DD-MM-YYYY format.\n\n"
            "Example: 25-08-2026"
        )


# ============================================================
# ADD TRANSACTION
# ============================================================

def add_new_transaction():

    window = tk.Toplevel(root)

    window.title(
        "Add Transaction"
    )

    window.geometry(
        "470x680"
    )

    window.resizable(
        False,
        False
    )

    tk.Label(
        window,
        text="ADD TRANSACTION",
        font=("Arial", 18, "bold")
    ).pack(
        pady=20
    )

    fields = {}

    for field in [
        "Date (DD-MM-YYYY)",
        "Description",
        "Category",
        "Amount"
    ]:

        tk.Label(
            window,
            text=field + ":"
        ).pack()

        entry = tk.Entry(
            window,
            width=35
        )

        entry.pack(
            pady=5
        )

        fields[field] = entry

    tk.Label(
        window,
        text="Currency:"
    ).pack()

    currency_var = tk.StringVar(
        value="INR - Indian Rupee"
    )

    ttk.Combobox(
        window,
        textvariable=currency_var,
        values=list(
            CURRENCIES.keys()
        ),
        state="readonly",
        width=32
    ).pack(
        pady=5
    )

    tk.Label(
        window,
        text="Type:"
    ).pack()

    type_var = tk.StringVar(
        value="Expense"
    )

    ttk.Combobox(
        window,
        textvariable=type_var,
        values=[
            "Income",
            "Expense"
        ],
        state="readonly",
        width=32
    ).pack(
        pady=5
    )

    tk.Label(
        window,
        text="Payment Method:"
    ).pack()

    payment_var = tk.StringVar(
        value="Cash"
    )

    ttk.Combobox(
        window,
        textvariable=payment_var,
        values=[
            "Cash",
            "UPI",
            "Debit Card",
            "Credit Card",
            "Bank Transfer",
            "Other"
        ],
        state="readonly",
        width=32
    ).pack(
        pady=5
    )

    def save():

        for field in [
            "Date (DD-MM-YYYY)",
            "Description",
            "Category",
            "Amount"
        ]:

            if not fields[field].get().strip():

                messagebox.showerror(
                    "Invalid Input",
                    f"{field} is required.",
                    parent=window
                )

                return

        try:

            validate_date(
                fields[
                    "Date (DD-MM-YYYY)"
                ].get()
            )

        except ValueError as error:

            messagebox.showerror(
                "Invalid Date",
                str(error),
                parent=window
            )

            return

        try:

            amount = parse_amount(
                fields["Amount"].get()
            )

        except ValueError as error:

            messagebox.showerror(
                "Invalid Amount",
                str(error),
                parent=window
            )

            return

        transaction = Transaction(
            None,
            fields[
                "Date (DD-MM-YYYY)"
            ].get().strip(),
            fields[
                "Description"
            ].get().strip(),
            fields[
                "Category"
            ].get().strip(),
            amount,
            currency_var.get(),
            type_var.get(),
            payment_var.get()
        )

        try:

            add_transaction(
                transaction.to_dict()
            )

            messagebox.showinfo(
                "Success",
                "Transaction added successfully!\n\n"
                f"Amount: "
                f"{format_currency(amount, currency_var.get())}",
                parent=window
            )

            window.destroy()

        except Exception as error:

            messagebox.showerror(
                "Database Error",
                str(error),
                parent=window
            )

    tk.Button(
        window,
        text="Save Transaction",
        width=20,
        height=2,
        command=save
    ).pack(
        pady=20
    )


# ============================================================
# VIEW TRANSACTIONS
# ============================================================

def view_transactions():

    try:
        transactions = get_all_transactions()

    except Exception as error:

        messagebox.showerror(
            "Database Error",
            str(error),
            parent=root
        )

        return

    window = tk.Toplevel(root)

    window.title(
        "View Transactions"
    )

    window.geometry(
        "1250x600"
    )

    window.minsize(
        900,
        500
    )

    tk.Label(
        window,
        text=f"TOTAL TRANSACTIONS: {len(transactions)}",
        font=("Arial", 18, "bold")
    ).pack(
        pady=15
    )

    frame = tk.Frame(
        window
    )

    frame.pack(
        fill=tk.BOTH,
        expand=True,
        padx=10,
        pady=10
    )

    columns = (
        "id",
        "date",
        "description",
        "category",
        "amount",
        "currency",
        "type",
        "payment"
    )

    y_scroll = tk.Scrollbar(
        frame,
        orient=tk.VERTICAL
    )

    x_scroll = tk.Scrollbar(
        frame,
        orient=tk.HORIZONTAL
    )

    table = ttk.Treeview(
        frame,
        columns=columns,
        show="headings",
        yscrollcommand=y_scroll.set,
        xscrollcommand=x_scroll.set
    )

    y_scroll.config(
        command=table.yview
    )

    x_scroll.config(
        command=table.xview
    )

    headings = {
        "id": "ID",
        "date": "Date",
        "description": "Description",
        "category": "Category",
        "amount": "Amount",
        "currency": "Currency",
        "type": "Type",
        "payment": "Payment Method"
    }

    for column in columns:

        table.heading(
            column,
            text=headings[column]
        )

        table.column(
            column,
            width=150
        )

    for transaction in transactions:

        table.insert(
            "",
            tk.END,
            values=(
                transaction[
                    "transaction_id"
                ],
                transaction[
                    "date"
                ],
                transaction[
                    "description"
                ],
                transaction[
                    "category"
                ],
                format_currency(
                    transaction[
                        "amount"
                    ],
                    transaction[
                        "currency"
                    ]
                ),
                transaction[
                    "currency"
                ],
                transaction[
                    "transaction_type"
                ],
                transaction[
                    "payment_method"
                ]
            )
        )

    table.pack(
        side=tk.LEFT,
        fill=tk.BOTH,
        expand=True
    )

    y_scroll.pack(
        side=tk.RIGHT,
        fill=tk.Y
    )

    x_scroll.pack(
        side=tk.BOTTOM,
        fill=tk.X
    )


# ============================================================
# SEARCH TRANSACTION BY ID
# ============================================================

def search_transaction():

    window = tk.Toplevel(root)

    window.title(
        "Search Transaction"
    )

    window.geometry(
        "550x500"
    )

    tk.Label(
        window,
        text="SEARCH TRANSACTION",
        font=("Arial", 18, "bold")
    ).pack(
        pady=20
    )

    tk.Label(
        window,
        text="Transaction ID:"
    ).pack()

    id_entry = tk.Entry(
        window,
        width=30
    )

    id_entry.pack(
        pady=10
    )

    result = tk.Text(
        window,
        width=60,
        height=18
    )

    result.pack(
        padx=15,
        pady=15
    )

    def search():

        try:

            transaction_id = int(
                id_entry.get().strip()
            )

        except ValueError:

            messagebox.showerror(
                "Invalid ID",
                "Enter a valid transaction ID.",
                parent=window
            )

            return

        try:

            transaction = find_transaction(
                transaction_id
            )

        except Exception as error:

            messagebox.showerror(
                "Database Error",
                str(error),
                parent=window
            )

            return

        result.delete(
            "1.0",
            tk.END
        )

        if transaction is None:

            result.insert(
                tk.END,
                "Transaction not found."
            )

            return

        result.insert(
            tk.END,
            "========== TRANSACTION ==========\n\n"
        )

        result.insert(
            tk.END,
            f"ID             : "
            f"{transaction['transaction_id']}\n"
        )

        result.insert(
            tk.END,
            f"Date           : "
            f"{transaction['date']}\n"
        )

        result.insert(
            tk.END,
            f"Description    : "
            f"{transaction['description']}\n"
        )

        result.insert(
            tk.END,
            f"Category       : "
            f"{transaction['category']}\n"
        )

        result.insert(
            tk.END,
            f"Amount         : "
            f"{format_currency(transaction['amount'], transaction['currency'])}\n"
        )

        result.insert(
            tk.END,
            f"Currency       : "
            f"{transaction['currency']}\n"
        )

        result.insert(
            tk.END,
            f"Type           : "
            f"{transaction['transaction_type']}\n"
        )

        result.insert(
            tk.END,
            f"Payment Method : "
            f"{transaction['payment_method']}\n"
        )

    tk.Button(
        window,
        text="Search",
        width=20,
        height=2,
        command=search
    ).pack(
        pady=10
    )


# ============================================================
# ADVANCED SEARCH + SORTING
# ============================================================

def advanced_transaction_search():

    window = tk.Toplevel(root)

    window.title(
        "Advanced Transaction Search"
    )

    window.geometry(
        "1300x800"
    )

    window.minsize(
        900,
        600
    )

    tk.Label(
        window,
        text="ADVANCED TRANSACTION SEARCH",
        font=("Arial", 20, "bold")
    ).pack(
        pady=20
    )

    search_frame = tk.LabelFrame(
        window,
        text="Search Filters",
        font=("Arial", 12, "bold"),
        padx=15,
        pady=15
    )

    search_frame.pack(
        fill="x",
        padx=20,
        pady=10
    )

    # ID
    tk.Label(
        search_frame,
        text="Transaction ID:"
    ).grid(
        row=0,
        column=0,
        padx=5,
        pady=5
    )

    id_entry = tk.Entry(
        search_frame,
        width=15
    )

    id_entry.grid(
        row=0,
        column=1,
        padx=5,
        pady=5
    )

    # Description
    tk.Label(
        search_frame,
        text="Description:"
    ).grid(
        row=0,
        column=2,
        padx=5,
        pady=5
    )

    description_entry = tk.Entry(
        search_frame,
        width=20
    )

    description_entry.grid(
        row=0,
        column=3,
        padx=5,
        pady=5
    )

    # Category
    tk.Label(
        search_frame,
        text="Category:"
    ).grid(
        row=0,
        column=4,
        padx=5,
        pady=5
    )

    category_entry = tk.Entry(
        search_frame,
        width=20
    )

    category_entry.grid(
        row=0,
        column=5,
        padx=5,
        pady=5
    )

    # Currency
    tk.Label(
        search_frame,
        text="Currency:"
    ).grid(
        row=1,
        column=0,
        padx=5,
        pady=5
    )

    currency_var = tk.StringVar(
        value="All"
    )

    ttk.Combobox(
        search_frame,
        textvariable=currency_var,
        values=[
            "All"
        ] + list(CURRENCIES.keys()),
        state="readonly",
        width=18
    ).grid(
        row=1,
        column=1,
        padx=5,
        pady=5
    )

    # Type
    tk.Label(
        search_frame,
        text="Type:"
    ).grid(
        row=1,
        column=2,
        padx=5,
        pady=5
    )

    type_var = tk.StringVar(
        value="All"
    )

    ttk.Combobox(
        search_frame,
        textvariable=type_var,
        values=[
            "All",
            "Income",
            "Expense"
        ],
        state="readonly",
        width=18
    ).grid(
        row=1,
        column=3,
        padx=5,
        pady=5
    )

    # Date
    tk.Label(
        search_frame,
        text="Date:"
    ).grid(
        row=1,
        column=4,
        padx=5,
        pady=5
    )

    date_entry = tk.Entry(
        search_frame,
        width=20
    )

    date_entry.grid(
        row=1,
        column=5,
        padx=5,
        pady=5
    )

    tk.Label(
        search_frame,
        text="DD-MM-YYYY"
    ).grid(
        row=2,
        column=5
    )

    # Sort
    tk.Label(
        search_frame,
        text="Sort By:"
    ).grid(
        row=3,
        column=0,
        padx=5,
        pady=8
    )

    sort_var = tk.StringVar(
        value="ID"
    )

    ttk.Combobox(
        search_frame,
        textvariable=sort_var,
        values=[
            "ID",
            "Date",
            "Description",
            "Category",
            "Amount",
            "Currency",
            "Type"
        ],
        state="readonly",
        width=18
    ).grid(
        row=3,
        column=1,
        padx=5,
        pady=8
    )

    # Order
    tk.Label(
        search_frame,
        text="Order:"
    ).grid(
        row=3,
        column=2,
        padx=5,
        pady=8
    )

    order_var = tk.StringVar(
        value="Ascending"
    )

    ttk.Combobox(
        search_frame,
        textvariable=order_var,
        values=[
            "Ascending",
            "Descending"
        ],
        state="readonly",
        width=18
    ).grid(
        row=3,
        column=3,
        padx=5,
        pady=8
    )

    # --------------------------------------------------------
    # TABLE
    # --------------------------------------------------------

    table_frame = tk.Frame(
        window
    )

    table_frame.pack(
        fill=tk.BOTH,
        expand=True,
        padx=20,
        pady=10
    )

    columns = (
        "id",
        "date",
        "description",
        "category",
        "amount",
        "currency",
        "type",
        "payment"
    )

    y_scroll = tk.Scrollbar(
        table_frame,
        orient=tk.VERTICAL
    )

    x_scroll = tk.Scrollbar(
        table_frame,
        orient=tk.HORIZONTAL
    )

    table = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings",
        yscrollcommand=y_scroll.set,
        xscrollcommand=x_scroll.set
    )

    y_scroll.config(
        command=table.yview
    )

    x_scroll.config(
        command=table.xview
    )

    headings = {
        "id": "ID",
        "date": "Date",
        "description": "Description",
        "category": "Category",
        "amount": "Amount",
        "currency": "Currency",
        "type": "Type",
        "payment": "Payment Method"
    }

    for column in columns:

        table.heading(
            column,
            text=headings[column]
        )

        table.column(
            column,
            width=150
        )

    table.pack(
        side=tk.LEFT,
        fill=tk.BOTH,
        expand=True
    )

    y_scroll.pack(
        side=tk.RIGHT,
        fill=tk.Y
    )

    x_scroll.pack(
        side=tk.BOTTOM,
        fill=tk.X
    )

    result_label = tk.Label(
        window,
        text="Found 0 transaction(s)",
        font=("Arial", 11, "bold")
    )

    result_label.pack(
        pady=5
    )

    # --------------------------------------------------------
    # SEARCH
    # --------------------------------------------------------

    def search():

        try:

            all_transactions = (
                get_all_transactions()
            )

        except Exception as error:

            messagebox.showerror(
                "Database Error",
                str(error),
                parent=window
            )

            return

        for item in table.get_children():

            table.delete(
                item
            )

        id_text = (
            id_entry.get().strip()
        )

        description_text = (
            description_entry
            .get()
            .strip()
            .lower()
        )

        category_text = (
            category_entry
            .get()
            .strip()
            .lower()
        )

        selected_currency = (
            currency_var.get()
        )

        selected_type = (
            type_var.get()
        )

        selected_date = (
            date_entry
            .get()
            .strip()
        )

        transaction_id = None

        if id_text:

            try:

                transaction_id = int(
                    id_text
                )

            except ValueError:

                messagebox.showerror(
                    "Invalid ID",
                    "Transaction ID must be a number.",
                    parent=window
                )

                return

        if selected_date:

            try:

                validate_date(
                    selected_date
                )

            except ValueError as error:

                messagebox.showerror(
                    "Invalid Date",
                    str(error),
                    parent=window
                )

                return

        results = []

        for transaction in all_transactions:

            if (
                transaction_id is not None
                and
                transaction[
                    "transaction_id"
                ] != transaction_id
            ):
                continue

            if (
                description_text
                and
                description_text
                not in transaction[
                    "description"
                ].lower()
            ):
                continue

            if (
                category_text
                and
                category_text
                not in transaction[
                    "category"
                ].lower()
            ):
                continue

            if (
                selected_currency != "All"
                and
                transaction[
                    "currency"
                ] != selected_currency
            ):
                continue

            if (
                selected_type != "All"
                and
                transaction[
                    "transaction_type"
                ] != selected_type
            ):
                continue

            if (
                selected_date
                and
                transaction[
                    "date"
                ] != selected_date
            ):
                continue

            results.append(
                transaction
            )

        # ----------------------------------------------------
        # SORT
        # ----------------------------------------------------

        sort_by = sort_var.get()

        ascending = (
            order_var.get()
            == "Ascending"
        )

        if sort_by == "ID":

            results.sort(
                key=lambda item:
                item["transaction_id"],
                reverse=not ascending
            )

        elif sort_by == "Date":

            def date_key(item):

                try:

                    return datetime.strptime(
                        item["date"],
                        "%d-%m-%Y"
                    )

                except ValueError:

                    return datetime.min

            results.sort(
                key=date_key,
                reverse=not ascending
            )

        elif sort_by == "Description":

            results.sort(
                key=lambda item:
                item["description"].lower(),
                reverse=not ascending
            )

        elif sort_by == "Category":

            results.sort(
                key=lambda item:
                item["category"].lower(),
                reverse=not ascending
            )

        elif sort_by == "Amount":

            results.sort(
                key=lambda item:
                item["amount"],
                reverse=not ascending
            )

        elif sort_by == "Currency":

            results.sort(
                key=lambda item:
                item["currency"].lower(),
                reverse=not ascending
            )

        elif sort_by == "Type":

            results.sort(
                key=lambda item:
                item["transaction_type"].lower(),
                reverse=not ascending
            )

        # ----------------------------------------------------
        # DISPLAY
        # ----------------------------------------------------

        for transaction in results:

            table.insert(
                "",
                tk.END,
                values=(
                    transaction[
                        "transaction_id"
                    ],
                    transaction[
                        "date"
                    ],
                    transaction[
                        "description"
                    ],
                    transaction[
                        "category"
                    ],
                    format_currency(
                        transaction[
                            "amount"
                        ],
                        transaction[
                            "currency"
                        ]
                    ),
                    transaction[
                        "currency"
                    ],
                    transaction[
                        "transaction_type"
                    ],
                    transaction[
                        "payment_method"
                    ]
                )
            )

        result_label.config(
            text=(
                f"Found {len(results)} "
                f"transaction(s)"
            )
        )

    # --------------------------------------------------------
    # CLEAR
    # --------------------------------------------------------

    def clear_search():

        id_entry.delete(
            0,
            tk.END
        )

        description_entry.delete(
            0,
            tk.END
        )

        category_entry.delete(
            0,
            tk.END
        )

        currency_var.set(
            "All"
        )

        type_var.set(
            "All"
        )

        date_entry.delete(
            0,
            tk.END
        )

        sort_var.set(
            "ID"
        )

        order_var.set(
            "Ascending"
        )

        for item in table.get_children():

            table.delete(
                item
            )

        result_label.config(
            text="Found 0 transaction(s)"
        )

    button_frame = tk.Frame(
        window
    )

    button_frame.pack(
        pady=10
    )

    tk.Button(
        button_frame,
        text="Search",
        width=18,
        height=2,
        command=search
    ).grid(
        row=0,
        column=0,
        padx=10
    )

    tk.Button(
        button_frame,
        text="Clear",
        width=18,
        height=2,
        command=clear_search
    ).grid(
        row=0,
        column=1,
        padx=10
    )


# ============================================================
# UPDATE TRANSACTION
# ============================================================

def update_existing_transaction():

    window = tk.Toplevel(root)

    window.title(
        "Update Transaction"
    )

    window.geometry(
        "520x700"
    )

    window.resizable(
        False,
        False
    )

    tk.Label(
        window,
        text="UPDATE TRANSACTION",
        font=("Arial", 18, "bold")
    ).pack(
        pady=20
    )

    tk.Label(
        window,
        text="Transaction ID:"
    ).pack()

    id_entry = tk.Entry(
        window,
        width=30
    )

    id_entry.pack(
        pady=5
    )

    entries = {}

    for field in [
        "Date",
        "Description",
        "Category",
        "Amount"
    ]:

        tk.Label(
            window,
            text=field + ":"
        ).pack()

        entry = tk.Entry(
            window,
            width=35
        )

        entry.pack(
            pady=4
        )

        entries[field] = entry

    tk.Label(
        window,
        text="Currency:"
    ).pack()

    currency_var = tk.StringVar(
        value="INR - Indian Rupee"
    )

    ttk.Combobox(
        window,
        textvariable=currency_var,
        values=list(
            CURRENCIES.keys()
        ),
        state="readonly",
        width=32
    ).pack(
        pady=5
    )

    tk.Label(
        window,
        text="Type:"
    ).pack()

    type_var = tk.StringVar(
        value="Expense"
    )

    ttk.Combobox(
        window,
        textvariable=type_var,
        values=[
            "Income",
            "Expense"
        ],
        state="readonly",
        width=32
    ).pack(
        pady=5
    )

    tk.Label(
        window,
        text="Payment Method:"
    ).pack()

    payment_var = tk.StringVar(
        value="Cash"
    )

    ttk.Combobox(
        window,
        textvariable=payment_var,
        values=[
            "Cash",
            "UPI",
            "Debit Card",
            "Credit Card",
            "Bank Transfer",
            "Other"
        ],
        state="readonly",
        width=32
    ).pack(
        pady=5
    )

    def load_transaction():

        try:

            transaction_id = int(
                id_entry.get().strip()
            )

        except ValueError:

            messagebox.showerror(
                "Invalid ID",
                "Enter a valid transaction ID.",
                parent=window
            )

            return

        try:

            transaction = find_transaction(
                transaction_id
            )

        except Exception as error:

            messagebox.showerror(
                "Database Error",
                str(error),
                parent=window
            )

            return

        if transaction is None:

            messagebox.showerror(
                "Not Found",
                "Transaction not found.",
                parent=window
            )

            return

        entries["Date"].delete(
            0,
            tk.END
        )

        entries["Date"].insert(
            0,
            transaction["date"]
        )

        entries["Description"].delete(
            0,
            tk.END
        )

        entries["Description"].insert(
            0,
            transaction["description"]
        )

        entries["Category"].delete(
            0,
            tk.END
        )

        entries["Category"].insert(
            0,
            transaction["category"]
        )

        entries["Amount"].delete(
            0,
            tk.END
        )

        entries["Amount"].insert(
            0,
            transaction["amount"]
        )

        currency_var.set(
            transaction["currency"]
        )

        type_var.set(
            transaction["transaction_type"]
        )

        payment_var.set(
            transaction["payment_method"]
        )

    def save_changes():

        try:

            transaction_id = int(
                id_entry.get().strip()
            )

        except ValueError:

            messagebox.showerror(
                "Invalid ID",
                "Enter a valid transaction ID.",
                parent=window
            )

            return

        for field in [
            "Date",
            "Description",
            "Category",
            "Amount"
        ]:

            if not entries[field].get().strip():

                messagebox.showerror(
                    "Invalid Input",
                    f"{field} is required.",
                    parent=window
                )

                return

        try:

            validate_date(
                entries["Date"].get()
            )

        except ValueError as error:

            messagebox.showerror(
                "Invalid Date",
                str(error),
                parent=window
            )

            return

        try:

            amount = parse_amount(
                entries["Amount"].get()
            )

        except ValueError as error:

            messagebox.showerror(
                "Invalid Amount",
                str(error),
                parent=window
            )

            return

        transaction = Transaction(
            transaction_id,
            entries["Date"].get().strip(),
            entries["Description"].get().strip(),
            entries["Category"].get().strip(),
            amount,
            currency_var.get(),
            type_var.get(),
            payment_var.get()
        )

        try:

            success = update_transaction(
                transaction.to_dict()
            )

        except Exception as error:

            messagebox.showerror(
                "Database Error",
                str(error),
                parent=window
            )

            return

        if success:

            messagebox.showinfo(
                "Success",
                "Transaction updated successfully.",
                parent=window
            )

            window.destroy()

        else:

            messagebox.showerror(
                "Error",
                "Transaction could not be updated.",
                parent=window
            )

    tk.Button(
        window,
        text="Load Transaction",
        width=20,
        height=2,
        command=load_transaction
    ).pack(
        pady=10
    )

    tk.Button(
        window,
        text="Save Changes",
        width=20,
        height=2,
        command=save_changes
    ).pack(
        pady=15
    )


# ============================================================
# DELETE TRANSACTION
# ============================================================

def delete_transaction_menu():

    window = tk.Toplevel(root)

    window.title(
        "Delete Transaction"
    )

    window.geometry(
        "450x420"
    )

    window.resizable(
        False,
        False
    )

    tk.Label(
        window,
        text="DELETE TRANSACTION",
        font=("Arial", 18, "bold")
    ).pack(
        pady=20
    )

    tk.Label(
        window,
        text="Transaction ID:"
    ).pack()

    id_entry = tk.Entry(
        window,
        width=30
    )

    id_entry.pack(
        pady=10
    )

    def delete_one():

        try:

            transaction_id = int(
                id_entry.get().strip()
            )

        except ValueError:

            messagebox.showerror(
                "Invalid ID",
                "Enter a valid transaction ID.",
                parent=window
            )

            return

        transaction = find_transaction(
            transaction_id
        )

        if transaction is None:

            messagebox.showerror(
                "Not Found",
                "Transaction not found.",
                parent=window
            )

            return

        confirmation = messagebox.askyesno(
            "Confirm Delete",

            f"ID: {transaction_id}\n"
            f"Description: {transaction['description']}\n"
            f"Amount: "
            f"{format_currency(transaction['amount'], transaction['currency'])}\n\n"
            "Delete this transaction?",

            parent=window
        )

        if not confirmation:
            return

        try:

            success = delete_transaction(
                transaction_id
            )

        except Exception as error:

            messagebox.showerror(
                "Database Error",
                str(error),
                parent=window
            )

            return

        if success:

            messagebox.showinfo(
                "Success",
                "Transaction deleted successfully.",
                parent=window
            )

            window.destroy()

        else:

            messagebox.showerror(
                "Error",
                "Transaction could not be deleted.",
                parent=window
            )

    def delete_all():

        transactions = get_all_transactions()

        total = len(
            transactions
        )

        if total == 0:

            messagebox.showinfo(
                "No Transactions",
                "There are no transactions.",
                parent=window
            )

            return

        confirmation = messagebox.askyesno(
            "Delete All",

            f"There are {total} transactions.\n\n"
            "Delete all transactions?",

            parent=window
        )

        if not confirmation:
            return

        try:

            deleted = delete_all_transactions()

        except Exception as error:

            messagebox.showerror(
                "Database Error",
                str(error),
                parent=window
            )

            return

        messagebox.showinfo(
            "Success",

            f"All {deleted} transactions deleted.\n\n"
            "The next transaction will start from ID 1.",

            parent=window
        )

        window.destroy()

    tk.Button(
        window,
        text="Delete One Transaction",
        width=25,
        height=2,
        command=delete_one
    ).pack(
        pady=10
    )

    tk.Button(
        window,
        text="Delete All Transactions",
        width=25,
        height=2,
        command=delete_all
    ).pack(
        pady=10
    )


# ============================================================
# FINANCIAL SUMMARY
# ============================================================

def show_summary():

    try:

        summaries = get_summary()

    except Exception as error:

        messagebox.showerror(
            "Database Error",
            str(error),
            parent=root
        )

        return

    window = tk.Toplevel(root)

    window.title(
        "Financial Summary"
    )

    window.geometry(
        "700x550"
    )

    result = tk.Text(
        window,
        width=75,
        height=28
    )

    result.pack(
        padx=20,
        pady=20
    )

    if not summaries:

        result.insert(
            tk.END,
            "No transactions found."
        )

    else:

        for summary in summaries:

            currency = summary[
                "currency"
            ]

            result.insert(
                tk.END,

                f"CURRENCY: {currency}\n"

                f"Income   : "
                f"{format_currency(summary['income'], currency)}\n"

                f"Expenses : "
                f"{format_currency(summary['expenses'], currency)}\n"

                f"Balance  : "
                f"{format_currency(summary['balance'], currency)}\n"

                + "-" * 60
                + "\n"
            )

    result.config(
        state=tk.DISABLED
    )


# ============================================================
# FINANCIAL DASHBOARD
# ============================================================

def financial_dashboard():

    window = tk.Toplevel(root)

    window.title(
        "Financial Dashboard"
    )

    window.geometry(
        "950x750"
    )

    window.minsize(
        700,
        500
    )

    window.resizable(
        True,
        True
    )

    tk.Label(
        window,
        text="FINANCIAL DASHBOARD",
        font=("Arial", 22, "bold")
    ).pack(
        pady=20
    )

    # --------------------------------------------------------
    # SCROLLABLE DASHBOARD
    # --------------------------------------------------------

    main_frame = tk.Frame(
        window
    )

    main_frame.pack(
        fill=tk.BOTH,
        expand=True
    )

    canvas = tk.Canvas(
        main_frame
    )

    canvas.pack(
        side=tk.LEFT,
        fill=tk.BOTH,
        expand=True
    )

    scrollbar = tk.Scrollbar(
        main_frame,
        orient=tk.VERTICAL,
        command=canvas.yview
    )

    scrollbar.pack(
        side=tk.RIGHT,
        fill=tk.Y
    )

    canvas.configure(
        yscrollcommand=scrollbar.set
    )

    dashboard_frame = tk.Frame(
        canvas
    )

    canvas_window = canvas.create_window(
        (0, 0),
        window=dashboard_frame,
        anchor="nw"
    )

    def update_dashboard_scroll(
        event=None
    ):

        canvas.configure(
            scrollregion=canvas.bbox("all")
        )

    dashboard_frame.bind(
        "<Configure>",
        update_dashboard_scroll
    )

    def resize_dashboard(
        event
    ):

        canvas.itemconfig(
            canvas_window,
            width=event.width
        )

    canvas.bind(
        "<Configure>",
        resize_dashboard
    )

    def dashboard_mouse_wheel(
        event
    ):

        canvas.yview_scroll(
            int(-1 * (event.delta / 120)),
            "units"
        )

    canvas.bind(
        "<Enter>",
        lambda event:
        canvas.bind_all(
            "<MouseWheel>",
            dashboard_mouse_wheel
        )
    )

    canvas.bind(
        "<Leave>",
        lambda event:
        canvas.unbind_all(
            "<MouseWheel>"
        )
    )

    # --------------------------------------------------------
    # GET DATA
    # --------------------------------------------------------

    try:

        normal_summary = get_summary()
        recurring_data = get_recurring_summary()

    except Exception as error:

        messagebox.showerror(
            "Database Error",
            str(error),
            parent=window
        )

        window.destroy()

        return

    # --------------------------------------------------------
    # RECURRING TOTALS
    # --------------------------------------------------------

    monthly_income = {}
    monthly_expense = {}

    yearly_income = {}
    yearly_expense = {}

    for row in recurring_data:

        try:

            (
                currency,
                record_type,
                frequency,
                amount
            ) = row

        except (
            ValueError,
            TypeError
        ):

            continue

        amount = float(
            amount or 0
        )

        if frequency == "Monthly":

            if record_type == "Income":

                monthly_income[
                    currency
                ] = (
                    monthly_income.get(
                        currency,
                        0
                    )
                    + amount
                )

            elif record_type == "Expense":

                monthly_expense[
                    currency
                ] = (
                    monthly_expense.get(
                        currency,
                        0
                    )
                    + amount
                )

        elif frequency == "Yearly":

            if record_type == "Income":

                yearly_income[
                    currency
                ] = (
                    yearly_income.get(
                        currency,
                        0
                    )
                    + amount
                )

            elif record_type == "Expense":

                yearly_expense[
                    currency
                ] = (
                    yearly_expense.get(
                        currency,
                        0
                    )
                    + amount
                )

    # --------------------------------------------------------
    # CURRENCIES
    # --------------------------------------------------------

    currencies = set()

    for item in normal_summary:

        try:

            currencies.add(
                item["currency"]
            )

        except (
            KeyError,
            TypeError
        ):

            pass

    currencies.update(
        monthly_income.keys()
    )

    currencies.update(
        monthly_expense.keys()
    )

    currencies.update(
        yearly_income.keys()
    )

    currencies.update(
        yearly_expense.keys()
    )

    if not currencies:

        tk.Label(
            dashboard_frame,
            text="No financial records found.",
            font=("Arial", 16)
        ).pack(
            pady=60
        )

        return

    # --------------------------------------------------------
    # DISPLAY DASHBOARD
    # --------------------------------------------------------

    for currency in sorted(
        currencies
    ):

        normal_income = 0
        normal_expense = 0

        for item in normal_summary:

            try:

                if item[
                    "currency"
                ] == currency:

                    normal_income = float(
                        item.get(
                            "income",
                            0
                        ) or 0
                    )

                    normal_expense = float(
                        item.get(
                            "expenses",
                            0
                        ) or 0
                    )

                    break

            except (
                KeyError,
                TypeError,
                ValueError
            ):

                continue

        normal_balance = (
            normal_income
            -
            normal_expense
        )

        month_income = (
            monthly_income.get(
                currency,
                0
            )
        )

        month_expense = (
            monthly_expense.get(
                currency,
                0
            )
        )

        month_saving = (
            month_income
            -
            month_expense
        )

        direct_year_income = (
            yearly_income.get(
                currency,
                0
            )
        )

        direct_year_expense = (
            yearly_expense.get(
                currency,
                0
            )
        )

        recurring_year_income = (
            month_income * 12
            +
            direct_year_income
        )

        recurring_year_expense = (
            month_expense * 12
            +
            direct_year_expense
        )

        year_saving = (
            recurring_year_income
            -
            recurring_year_expense
        )

        # ----------------------------------------------------
        # CURRENCY NAME
        # ----------------------------------------------------

        tk.Label(
            dashboard_frame,
            text=currency,
            font=("Arial", 20, "bold")
        ).pack(
            pady=(25, 10)
        )

        # ----------------------------------------------------
        # TRANSACTION SUMMARY
        # ----------------------------------------------------

        transaction_frame = tk.LabelFrame(
            dashboard_frame,
            text="Transaction Summary",
            font=("Arial", 12, "bold"),
            padx=20,
            pady=15
        )

        transaction_frame.pack(
            fill="x",
            padx=30,
            pady=8
        )

        tk.Label(
            transaction_frame,
            text=(
                "Income: "
                +
                format_currency(
                    normal_income,
                    currency
                )
            ),
            font=("Arial", 13)
        ).pack(
            pady=5
        )

        tk.Label(
            transaction_frame,
            text=(
                "Expenses: "
                +
                format_currency(
                    normal_expense,
                    currency
                )
            ),
            font=("Arial", 13)
        ).pack(
            pady=5
        )

        tk.Label(
            transaction_frame,
            text=(
                "Balance: "
                +
                format_currency(
                    normal_balance,
                    currency
                )
            ),
            font=("Arial", 13, "bold")
        ).pack(
            pady=5
        )

        # ----------------------------------------------------
        # MONTHLY
        # ----------------------------------------------------

        monthly_frame = tk.LabelFrame(
            dashboard_frame,
            text="Monthly Income & Expense",
            font=("Arial", 12, "bold"),
            padx=20,
            pady=15
        )

        monthly_frame.pack(
            fill="x",
            padx=30,
            pady=8
        )

        tk.Label(
            monthly_frame,
            text=(
                "Monthly Income: "
                +
                format_currency(
                    month_income,
                    currency
                )
            ),
            font=("Arial", 13)
        ).pack(
            pady=5
        )

        tk.Label(
            monthly_frame,
            text=(
                "Monthly Expense: "
                +
                format_currency(
                    month_expense,
                    currency
                )
            ),
            font=("Arial", 13)
        ).pack(
            pady=5
        )

        tk.Label(
            monthly_frame,
            text=(
                "Monthly Saving: "
                +
                format_currency(
                    month_saving,
                    currency
                )
            ),
            font=("Arial", 13, "bold")
        ).pack(
            pady=5
        )

        # ----------------------------------------------------
        # YEARLY
        # ----------------------------------------------------

        yearly_frame = tk.LabelFrame(
            dashboard_frame,
            text="Yearly Income & Expense",
            font=("Arial", 12, "bold"),
            padx=20,
            pady=15
        )

        yearly_frame.pack(
            fill="x",
            padx=30,
            pady=8
        )

        tk.Label(
            yearly_frame,
            text=(
                "Yearly Income: "
                +
                format_currency(
                    recurring_year_income,
                    currency
                )
            ),
            font=("Arial", 13)
        ).pack(
            pady=5
        )

        tk.Label(
            yearly_frame,
            text=(
                "Yearly Expense: "
                +
                format_currency(
                    recurring_year_expense,
                    currency
                )
            ),
            font=("Arial", 13)
        ).pack(
            pady=5
        )

        tk.Label(
            yearly_frame,
            text=(
                "Yearly Saving: "
                +
                format_currency(
                    year_saving,
                    currency
                )
            ),
            font=("Arial", 13, "bold")
        ).pack(
            pady=5
        )

        ttk.Separator(
            dashboard_frame,
            orient=tk.HORIZONTAL
        ).pack(
            fill="x",
            padx=30,
            pady=20
        )


# ============================================================
# MONTHLY REPORT
# ============================================================

def monthly_report():

    window = tk.Toplevel(root)

    window.title(
        "Monthly Report"
    )

    window.geometry(
        "800x650"
    )

    tk.Label(
        window,
        text="MONTHLY REPORT",
        font=("Arial", 18, "bold")
    ).pack(
        pady=20
    )

    controls = tk.Frame(
        window
    )

    controls.pack(
        pady=5
    )

    tk.Label(
        controls,
        text="Month:"
    ).grid(
        row=0,
        column=0,
        padx=5
    )

    month_entry = tk.Entry(
        controls,
        width=15
    )

    month_entry.grid(
        row=0,
        column=1,
        padx=5
    )

    tk.Label(
        controls,
        text="Year:"
    ).grid(
        row=0,
        column=2,
        padx=5
    )

    year_entry = tk.Entry(
        controls,
        width=15
    )

    year_entry.grid(
        row=0,
        column=3,
        padx=5
    )

    result = tk.Text(
        window,
        width=85,
        height=30
    )

    result.pack(
        padx=20,
        pady=20
    )

    def generate():

        try:

            month = int(
                month_entry.get().strip()
            )

            year = int(
                year_entry.get().strip()
            )

            if not 1 <= month <= 12:
                raise ValueError

            if year < 2000:
                raise ValueError

        except ValueError:

            messagebox.showerror(
                "Invalid Input",
                "Enter a valid month and year.",
                parent=window
            )

            return

        try:

            reports = get_monthly_summary(
                month,
                year
            )

        except Exception as error:

            messagebox.showerror(
                "Database Error",
                str(error),
                parent=window
            )

            return

        result.delete(
            "1.0",
            tk.END
        )

        if not reports:

            result.insert(
                tk.END,
                "No transactions found for this month."
            )

            return

        for report in reports:

            currency = report[
                "currency"
            ]

            result.insert(
                tk.END,

                f"CURRENCY: {currency}\n"

                f"Income       : "
                f"{format_currency(report['income'], currency)}\n"

                f"Expenses     : "
                f"{format_currency(report['expenses'], currency)}\n"

                f"Balance      : "
                f"{format_currency(report['balance'], currency)}\n"

                f"Transactions : "
                f"{report['transactions']}\n"

                + "-" * 70
                + "\n"
            )

    tk.Button(
        controls,
        text="Generate",
        width=15,
        height=2,
        command=generate
    ).grid(
        row=0,
        column=4,
        padx=10
    )


# ============================================================
# CATEGORY REPORT
# ============================================================

def category_report():

    window = tk.Toplevel(root)

    window.title(
        "Category Report"
    )

    window.geometry(
        "900x600"
    )

    tk.Label(
        window,
        text="CATEGORY-WISE EXPENSE REPORT",
        font=("Arial", 18, "bold")
    ).pack(
        pady=20
    )

    frame = tk.Frame(
        window
    )

    frame.pack(
        fill=tk.BOTH,
        expand=True,
        padx=20,
        pady=20
    )

    columns = (
        "currency",
        "category",
        "amount",
        "transactions"
    )

    y_scroll = tk.Scrollbar(
        frame,
        orient=tk.VERTICAL
    )

    table = ttk.Treeview(
        frame,
        columns=columns,
        show="headings",
        yscrollcommand=y_scroll.set
    )

    y_scroll.config(
        command=table.yview
    )

    table.heading(
        "currency",
        text="Currency"
    )

    table.heading(
        "category",
        text="Category"
    )

    table.heading(
        "amount",
        text="Total Amount"
    )

    table.heading(
        "transactions",
        text="Transactions"
    )

    for column in columns:

        table.column(
            column,
            width=180
        )

    try:

        categories = get_category_summary()

    except Exception as error:

        messagebox.showerror(
            "Database Error",
            str(error),
            parent=window
        )

        window.destroy()

        return

    for item in categories:

        table.insert(
            "",
            tk.END,
            values=(
                item["currency"],
                item["category"],
                format_currency(
                    item["amount"],
                    item["currency"]
                ),
                item["transactions"]
            )
        )

    table.pack(
        side=tk.LEFT,
        fill=tk.BOTH,
        expand=True
    )

    y_scroll.pack(
        side=tk.RIGHT,
        fill=tk.Y
    )


# ============================================================
# ADD MONTHLY / YEARLY RECORD
# ============================================================

def add_recurring_record_window():

    window = tk.Toplevel(root)

    window.title(
        "Add Monthly / Yearly Record"
    )

    window.geometry(
        "520x650"
    )

    tk.Label(
        window,
        text="MONTHLY / YEARLY INCOME & EXPENSE",
        font=("Arial", 17, "bold")
    ).pack(
        pady=20
    )

    fields = {}

    for field in [
        "Description",
        "Category",
        "Amount",
        "Start Year"
    ]:

        tk.Label(
            window,
            text=field + ":"
        ).pack()

        entry = tk.Entry(
            window,
            width=35
        )

        entry.pack(
            pady=5
        )

        fields[field] = entry

    tk.Label(
        window,
        text="Currency:"
    ).pack()

    currency_var = tk.StringVar(
        value="INR - Indian Rupee"
    )

    ttk.Combobox(
        window,
        textvariable=currency_var,
        values=list(
            CURRENCIES.keys()
        ),
        state="readonly",
        width=32
    ).pack(
        pady=5
    )

    tk.Label(
        window,
        text="Type:"
    ).pack()

    type_var = tk.StringVar(
        value="Income"
    )

    ttk.Combobox(
        window,
        textvariable=type_var,
        values=[
            "Income",
            "Expense"
        ],
        state="readonly",
        width=32
    ).pack(
        pady=5
    )

    tk.Label(
        window,
        text="Frequency:"
    ).pack()

    frequency_var = tk.StringVar(
        value="Monthly"
    )

    ttk.Combobox(
        window,
        textvariable=frequency_var,
        values=[
            "Monthly",
            "Yearly"
        ],
        state="readonly",
        width=32
    ).pack(
        pady=5
    )

    def save():

        description = (
            fields[
                "Description"
            ]
            .get()
            .strip()
        )

        category = (
            fields[
                "Category"
            ]
            .get()
            .strip()
        )

        if not description:

            messagebox.showerror(
                "Invalid Input",
                "Description is required.",
                parent=window
            )

            return

        if not category:

            messagebox.showerror(
                "Invalid Input",
                "Category is required.",
                parent=window
            )

            return

        try:

            amount = parse_amount(
                fields[
                    "Amount"
                ].get()
            )

        except ValueError as error:

            messagebox.showerror(
                "Invalid Amount",
                str(error),
                parent=window
            )

            return

        try:

            start_year = int(
                fields[
                    "Start Year"
                ]
                .get()
                .strip()
            )

            if start_year < 2000:
                raise ValueError

        except ValueError:

            messagebox.showerror(
                "Invalid Year",
                "Enter a valid year.",
                parent=window
            )

            return

        record = RecurringRecord(
            None,
            description,
            category,
            amount,
            currency_var.get(),
            type_var.get(),
            frequency_var.get(),
            start_year
        )

        try:

            add_recurring_record(
                record.to_dict()
            )

            messagebox.showinfo(
                "Success",
                "Recurring record added successfully.",
                parent=window
            )

            window.destroy()

        except Exception as error:

            messagebox.showerror(
                "Database Error",
                str(error),
                parent=window
            )

    tk.Button(
        window,
        text="Save Record",
        width=20,
        height=2,
        command=save
    ).pack(
        pady=20
    )


# ============================================================
# VIEW MONTHLY / YEARLY RECORDS
# ============================================================

def view_recurring_records():

    try:

        records = (
            get_recurring_records()
        )

    except Exception as error:

        messagebox.showerror(
            "Database Error",
            str(error),
            parent=root
        )

        return

    window = tk.Toplevel(root)

    window.title(
        "Monthly / Yearly Records"
    )

    window.geometry(
        "1100x600"
    )

    tk.Label(
        window,
        text=(
            f"TOTAL RECURRING RECORDS: "
            f"{len(records)}"
        ),
        font=("Arial", 18, "bold")
    ).pack(
        pady=15
    )

    frame = tk.Frame(
        window
    )

    frame.pack(
        fill=tk.BOTH,
        expand=True
    )

    columns = (
        "id",
        "description",
        "category",
        "amount",
        "currency",
        "type",
        "frequency",
        "year"
    )

    y_scroll = tk.Scrollbar(
        frame,
        orient=tk.VERTICAL
    )

    x_scroll = tk.Scrollbar(
        frame,
        orient=tk.HORIZONTAL
    )

    table = ttk.Treeview(
        frame,
        columns=columns,
        show="headings",
        yscrollcommand=y_scroll.set,
        xscrollcommand=x_scroll.set
    )

    y_scroll.config(
        command=table.yview
    )

    x_scroll.config(
        command=table.xview
    )

    headings = {
        "id": "ID",
        "description": "Description",
        "category": "Category",
        "amount": "Amount",
        "currency": "Currency",
        "type": "Type",
        "frequency": "Frequency",
        "year": "Start Year"
    }

    for column in columns:

        table.heading(
            column,
            text=headings[column]
        )

        table.column(
            column,
            width=140
        )

    for record in records:

        table.insert(
            "",
            tk.END,
            values=(
                record["record_id"],
                record["description"],
                record["category"],
                format_currency(
                    record["amount"],
                    record["currency"]
                ),
                record["currency"],
                record["record_type"],
                record["frequency"],
                record["start_year"]
            )
        )

    table.pack(
        side=tk.LEFT,
        fill=tk.BOTH,
        expand=True
    )

    y_scroll.pack(
        side=tk.RIGHT,
        fill=tk.Y
    )

    x_scroll.pack(
        side=tk.BOTTOM,
        fill=tk.X
    )


# ============================================================
# UPDATE MONTHLY / YEARLY RECORD
# ============================================================

def update_recurring_record_window():

    window = tk.Toplevel(root)

    window.title(
        "Update Monthly / Yearly Record"
    )

    window.geometry(
        "520x720"
    )

    tk.Label(
        window,
        text="UPDATE MONTHLY / YEARLY RECORD",
        font=("Arial", 17, "bold")
    ).pack(
        pady=20
    )

    tk.Label(
        window,
        text="Record ID:"
    ).pack()

    id_entry = tk.Entry(
        window,
        width=30
    )

    id_entry.pack(
        pady=5
    )

    fields = {}

    for field in [
        "Description",
        "Category",
        "Amount",
        "Start Year"
    ]:

        tk.Label(
            window,
            text=field + ":"
        ).pack()

        entry = tk.Entry(
            window,
            width=35
        )

        entry.pack(
            pady=5
        )

        fields[field] = entry

    tk.Label(
        window,
        text="Currency:"
    ).pack()

    currency_var = tk.StringVar(
        value="INR - Indian Rupee"
    )

    ttk.Combobox(
        window,
        textvariable=currency_var,
        values=list(
            CURRENCIES.keys()
        ),
        state="readonly",
        width=32
    ).pack(
        pady=5
    )

    tk.Label(
        window,
        text="Type:"
    ).pack()

    type_var = tk.StringVar(
        value="Income"
    )

    ttk.Combobox(
        window,
        textvariable=type_var,
        values=[
            "Income",
            "Expense"
        ],
        state="readonly",
        width=32
    ).pack(
        pady=5
    )

    tk.Label(
        window,
        text="Frequency:"
    ).pack()

    frequency_var = tk.StringVar(
        value="Monthly"
    )

    ttk.Combobox(
        window,
        textvariable=frequency_var,
        values=[
            "Monthly",
            "Yearly"
        ],
        state="readonly",
        width=32
    ).pack(
        pady=5
    )

    def load_record():

        try:

            record_id = int(
                id_entry.get().strip()
            )

        except ValueError:

            messagebox.showerror(
                "Invalid ID",
                "Enter a valid record ID.",
                parent=window
            )

            return

        records = (
            get_recurring_records()
        )

        record = None

        for item in records:

            if item[
                "record_id"
            ] == record_id:

                record = item
                break

        if record is None:

            messagebox.showerror(
                "Not Found",
                "Recurring record not found.",
                parent=window
            )

            return

        fields[
            "Description"
        ].delete(
            0,
            tk.END
        )

        fields[
            "Description"
        ].insert(
            0,
            record["description"]
        )

        fields[
            "Category"
        ].delete(
            0,
            tk.END
        )

        fields[
            "Category"
        ].insert(
            0,
            record["category"]
        )

        fields[
            "Amount"
        ].delete(
            0,
            tk.END
        )

        fields[
            "Amount"
        ].insert(
            0,
            record["amount"]
        )

        fields[
            "Start Year"
        ].delete(
            0,
            tk.END
        )

        fields[
            "Start Year"
        ].insert(
            0,
            record["start_year"]
        )

        currency_var.set(
            record["currency"]
        )

        type_var.set(
            record["record_type"]
        )

        frequency_var.set(
            record["frequency"]
        )

    def save_changes():

        try:

            record_id = int(
                id_entry.get().strip()
            )

        except ValueError:

            messagebox.showerror(
                "Invalid ID",
                "Enter a valid record ID.",
                parent=window
            )

            return

        description = (
            fields[
                "Description"
            ]
            .get()
            .strip()
        )

        category = (
            fields[
                "Category"
            ]
            .get()
            .strip()
        )

        if not description:

            messagebox.showerror(
                "Invalid Input",
                "Description is required.",
                parent=window
            )

            return

        if not category:

            messagebox.showerror(
                "Invalid Input",
                "Category is required.",
                parent=window
            )

            return

        try:

            amount = parse_amount(
                fields[
                    "Amount"
                ].get()
            )

        except ValueError as error:

            messagebox.showerror(
                "Invalid Amount",
                str(error),
                parent=window
            )

            return

        try:

            start_year = int(
                fields[
                    "Start Year"
                ]
                .get()
                .strip()
            )

            if start_year < 2000:
                raise ValueError

        except ValueError:

            messagebox.showerror(
                "Invalid Year",
                "Enter a valid year.",
                parent=window
            )

            return

        record = RecurringRecord(
            record_id,
            description,
            category,
            amount,
            currency_var.get(),
            type_var.get(),
            frequency_var.get(),
            start_year
        )

        try:

            success = (
                update_recurring_record(
                    record.to_dict()
                )
            )

        except Exception as error:

            messagebox.showerror(
                "Database Error",
                str(error),
                parent=window
            )

            return

        if success:

            messagebox.showinfo(
                "Success",
                "Recurring record updated successfully.",
                parent=window
            )

            window.destroy()

        else:

            messagebox.showerror(
                "Error",
                "Record could not be updated.",
                parent=window
            )

    tk.Button(
        window,
        text="Load Record",
        width=20,
        height=2,
        command=load_record
    ).pack(
        pady=15
    )

    tk.Button(
        window,
        text="Save Changes",
        width=20,
        height=2,
        command=save_changes
    ).pack(
        pady=15
    )


# ============================================================
# MONTHLY / YEARLY REPORT
# ============================================================

def recurring_report():

    window = tk.Toplevel(root)

    window.title(
        "Monthly / Yearly Financial Report"
    )

    window.geometry(
        "900x700"
    )

    tk.Label(
        window,
        text="MONTHLY & YEARLY FINANCIAL REPORT",
        font=("Arial", 18, "bold")
    ).pack(
        pady=20
    )

    result = tk.Text(
        window,
        width=100,
        height=35
    )

    result.pack(
        padx=20,
        pady=20
    )

    try:

        summary = (
            get_recurring_summary()
        )

    except Exception as error:

        messagebox.showerror(
            "Database Error",
            str(error),
            parent=window
        )

        window.destroy()

        return

    monthly_income = {}
    monthly_expense = {}

    yearly_income = {}
    yearly_expense = {}

    for row in summary:

        try:

            (
                currency,
                record_type,
                frequency,
                amount
            ) = row

        except (
            ValueError,
            TypeError
        ):

            continue

        amount = float(
            amount or 0
        )

        if frequency == "Monthly":

            if record_type == "Income":

                monthly_income[
                    currency
                ] = (
                    monthly_income.get(
                        currency,
                        0
                    )
                    + amount
                )

            else:

                monthly_expense[
                    currency
                ] = (
                    monthly_expense.get(
                        currency,
                        0
                    )
                    + amount
                )

        elif frequency == "Yearly":

            if record_type == "Income":

                yearly_income[
                    currency
                ] = (
                    yearly_income.get(
                        currency,
                        0
                    )
                    + amount
                )

            else:

                yearly_expense[
                    currency
                ] = (
                    yearly_expense.get(
                        currency,
                        0
                    )
                    + amount
                )

    currencies = (
        set(monthly_income)
        |
        set(monthly_expense)
        |
        set(yearly_income)
        |
        set(yearly_expense)
    )

    if not currencies:

        result.insert(
            tk.END,
            "No recurring records found."
        )

        return

    for currency in sorted(
        currencies
    ):

        month_income = (
            monthly_income.get(
                currency,
                0
            )
        )

        month_expense = (
            monthly_expense.get(
                currency,
                0
            )
        )

        direct_year_income = (
            yearly_income.get(
                currency,
                0
            )
        )

        direct_year_expense = (
            yearly_expense.get(
                currency,
                0
            )
        )

        yearly_income_total = (
            month_income * 12
            +
            direct_year_income
        )

        yearly_expense_total = (
            month_expense * 12
            +
            direct_year_expense
        )

        monthly_saving = (
            month_income
            -
            month_expense
        )

        yearly_saving = (
            yearly_income_total
            -
            yearly_expense_total
        )

        result.insert(
            tk.END,

            f"CURRENCY: {currency}\n"

            + "=" * 90
            + "\n"

            f"Monthly Income   : "
            f"{format_currency(month_income, currency)}\n"

            f"Monthly Expense  : "
            f"{format_currency(month_expense, currency)}\n"

            f"Monthly Saving   : "
            f"{format_currency(monthly_saving, currency)}\n\n"

            f"Yearly Income    : "
            f"{format_currency(yearly_income_total, currency)}\n"

            f"Yearly Expense   : "
            f"{format_currency(yearly_expense_total, currency)}\n"

            f"Yearly Saving    : "
            f"{format_currency(yearly_saving, currency)}\n\n"

            + "-" * 90
            + "\n\n"
        )


# ============================================================
# YEARLY COMPARISON
# ============================================================

def yearly_comparison():

    window = tk.Toplevel(root)

    window.title(
        "Yearly Income & Expense Comparison"
    )

    window.geometry(
        "950x750"
    )

    tk.Label(
        window,
        text="YEARLY INCOME & EXPENSE COMPARISON",
        font=("Arial", 18, "bold")
    ).pack(
        pady=20
    )

    controls = tk.Frame(
        window
    )

    controls.pack(
        pady=10
    )

    tk.Label(
        controls,
        text="First Year:"
    ).grid(
        row=0,
        column=0,
        padx=5
    )

    first_year_entry = tk.Entry(
        controls,
        width=15
    )

    first_year_entry.grid(
        row=0,
        column=1,
        padx=5
    )

    tk.Label(
        controls,
        text="Second Year:"
    ).grid(
        row=0,
        column=2,
        padx=5
    )

    second_year_entry = tk.Entry(
        controls,
        width=15
    )

    second_year_entry.grid(
        row=0,
        column=3,
        padx=5
    )

    result = tk.Text(
        window,
        width=105,
        height=35
    )

    result.pack(
        padx=20,
        pady=20
    )

    def compare():

        try:

            first_year = int(
                first_year_entry
                .get()
                .strip()
            )

            second_year = int(
                second_year_entry
                .get()
                .strip()
            )

            if first_year < 2000:
                raise ValueError

            if second_year < 2000:
                raise ValueError

            if first_year == second_year:
                raise ValueError

        except ValueError:

            messagebox.showerror(
                "Invalid Year",
                "Enter two different valid years.",
                parent=window
            )

            return

        try:

            comparison = (
                get_yearly_comparison(
                    first_year,
                    second_year
                )
            )

        except Exception as error:

            messagebox.showerror(
                "Database Error",
                str(error),
                parent=window
            )

            return

        result.delete(
            "1.0",
            tk.END
        )

        if not comparison:

            result.insert(
                tk.END,
                "No recurring records found."
            )

            return

        for item in comparison:

            currency = item[
                "currency"
            ]

            income_change = item[
                "income_change"
            ]

            expense_change = item[
                "expense_change"
            ]

            savings_change = item[
                "savings_change"
            ]

            income_word = (
                "Increase"
                if income_change >= 0
                else "Decrease"
            )

            expense_word = (
                "Increase"
                if expense_change >= 0
                else "Decrease"
            )

            savings_word = (
                "Increase"
                if savings_change >= 0
                else "Decrease"
            )

            result.insert(
                tk.END,

                f"CURRENCY: {currency}\n"

                + "=" * 90
                + "\n\n"

                "INCOME\n"

                f"{first_year}: "
                f"{format_currency(item['year1_income'], currency)}\n"

                f"{second_year}: "
                f"{format_currency(item['year2_income'], currency)}\n"

                f"{income_word}: "
                f"{format_currency(abs(income_change), currency)}\n"

                f"Percentage Change: "
                f"{item['income_percentage']:.2f}%\n\n"

                "EXPENSE\n"

                f"{first_year}: "
                f"{format_currency(item['year1_expenses'], currency)}\n"

                f"{second_year}: "
                f"{format_currency(item['year2_expenses'], currency)}\n"

                f"{expense_word}: "
                f"{format_currency(abs(expense_change), currency)}\n"

                f"Percentage Change: "
                f"{item['expense_percentage']:.2f}%\n\n"

                "SAVINGS\n"

                f"{first_year}: "
                f"{format_currency(item['year1_savings'], currency)}\n"

                f"{second_year}: "
                f"{format_currency(item['year2_savings'], currency)}\n"

                f"{savings_word}: "
                f"{format_currency(abs(savings_change), currency)}\n"

                f"Percentage Change: "
                f"{item['savings_percentage']:.2f}%\n\n"

                + "-" * 90
                + "\n\n"
            )

    tk.Button(
        controls,
        text="Compare",
        width=18,
        height=2,
        command=compare
    ).grid(
        row=0,
        column=4,
        padx=10
    )


# ============================================================
# DELETE MONTHLY / YEARLY RECORDS
# ============================================================

def delete_recurring_records():

    window = tk.Toplevel(root)

    window.title(
        "Delete Monthly / Yearly Records"
    )

    window.geometry(
        "450x420"
    )

    tk.Label(
        window,
        text="DELETE RECURRING RECORD",
        font=("Arial", 18, "bold")
    ).pack(
        pady=20
    )

    tk.Label(
        window,
        text="Record ID:"
    ).pack()

    id_entry = tk.Entry(
        window,
        width=30
    )

    id_entry.pack(
        pady=10
    )

    def delete_one():

        try:

            record_id = int(
                id_entry.get().strip()
            )

        except ValueError:

            messagebox.showerror(
                "Invalid ID",
                "Enter a valid record ID.",
                parent=window
            )

            return

        try:

            success = delete_recurring_record(
                record_id
            )

        except Exception as error:

            messagebox.showerror(
                "Database Error",
                str(error),
                parent=window
            )

            return

        if success:

            messagebox.showinfo(
                "Success",
                "Recurring record deleted.",
                parent=window
            )

            window.destroy()

        else:

            messagebox.showerror(
                "Not Found",
                "Recurring record not found.",
                parent=window
            )

    def delete_all():

        try:

            records = (
                get_recurring_records()
            )

        except Exception as error:

            messagebox.showerror(
                "Database Error",
                str(error),
                parent=window
            )

            return

        if not records:

            messagebox.showinfo(
                "No Records",
                "There are no recurring records.",
                parent=window
            )

            return

        confirmation = messagebox.askyesno(
            "Delete All",

            f"There are {len(records)} records.\n\n"
            "Delete all recurring records?",

            parent=window
        )

        if not confirmation:
            return

        try:

            deleted = (
                delete_all_recurring_records()
            )

        except Exception as error:

            messagebox.showerror(
                "Database Error",
                str(error),
                parent=window
            )

            return

        messagebox.showinfo(
            "Success",

            f"All {deleted} recurring records deleted.",

            parent=window
        )

        window.destroy()

    tk.Button(
        window,
        text="Delete One",
        width=25,
        height=2,
        command=delete_one
    ).pack(
        pady=10
    )

    tk.Button(
        window,
        text="Delete All",
        width=25,
        height=2,
        command=delete_all
    ).pack(
        pady=10
    )


# ============================================================
# EXPORT TRANSACTIONS
# ============================================================

def export_transactions():

    try:

        rows = export_transactions_data()

    except Exception as error:

        messagebox.showerror(
            "Database Error",
            str(error),
            parent=root
        )

        return

    if not rows:

        messagebox.showinfo(
            "No Data",
            "There are no transactions to export."
        )

        return

    file_path = filedialog.asksaveasfilename(
        title="Save Transactions",
        defaultextension=".csv",
        initialfile="transactions.csv",
        filetypes=[
            ("CSV Files", "*.csv"),
            ("All Files", "*.*")
        ]
    )

    if not file_path:
        return

    try:

        with open(
            file_path,
            "w",
            newline="",
            encoding="utf-8-sig"
        ) as file:

            writer = csv.writer(
                file
            )

            writer.writerow([
                "Transaction ID",
                "Date",
                "Description",
                "Category",
                "Amount",
                "Currency",
                "Type",
                "Payment Method"
            ])

            writer.writerows(
                rows
            )

        messagebox.showinfo(
            "Export Successful",
            "Transactions exported successfully.\n\n"
            f"{file_path}"
        )

    except (
        OSError,
        csv.Error
    ) as error:

        messagebox.showerror(
            "Export Error",
            str(error)
        )


# ============================================================
# EXPORT MONTHLY / YEARLY
# ============================================================

def export_recurring_records():

    try:

        rows = export_recurring_data()

    except Exception as error:

        messagebox.showerror(
            "Database Error",
            str(error),
            parent=root
        )

        return

    if not rows:

        messagebox.showinfo(
            "No Data",
            "There are no monthly/yearly records to export."
        )

        return

    file_path = filedialog.asksaveasfilename(
        title="Save Monthly/Yearly Records",
        defaultextension=".csv",
        initialfile="recurring_records.csv",
        filetypes=[
            ("CSV Files", "*.csv"),
            ("All Files", "*.*")
        ]
    )

    if not file_path:
        return

    try:

        with open(
            file_path,
            "w",
            newline="",
            encoding="utf-8-sig"
        ) as file:

            writer = csv.writer(
                file
            )

            writer.writerow([
                "Record ID",
                "Description",
                "Category",
                "Amount",
                "Currency",
                "Type",
                "Frequency",
                "Start Year"
            ])

            writer.writerows(
                rows
            )

        messagebox.showinfo(
            "Export Successful",
            "Monthly/yearly records exported successfully.\n\n"
            f"{file_path}"
        )

    except (
        OSError,
        csv.Error
    ) as error:

        messagebox.showerror(
            "Export Error",
            str(error)
        )


# ============================================================
# BACKUP DATABASE
# ============================================================

def backup_database():

    database_file = "expenses.db"

    if not os.path.exists(
        database_file
    ):

        messagebox.showerror(
            "Backup Error",
            "expenses.db does not exist."
        )

        return

    backup_path = filedialog.asksaveasfilename(
        title="Backup Database",
        defaultextension=".db",
        initialfile="expenses_backup.db",
        filetypes=[
            ("SQLite Database", "*.db"),
            ("All Files", "*.*")
        ]
    )

    if not backup_path:
        return

    try:

        if (
            os.path.abspath(
                backup_path
            )
            ==
            os.path.abspath(
                database_file
            )
        ):

            messagebox.showerror(
                "Backup Error",
                "Choose a different backup filename."
            )

            return

        shutil.copy2(
            database_file,
            backup_path
        )

        messagebox.showinfo(
            "Backup Successful",
            "Database backup created successfully.\n\n"
            f"{backup_path}"
        )

    except (
        OSError,
        shutil.Error
    ) as error:

        messagebox.showerror(
            "Backup Error",
            str(error)
        )


# ============================================================
# EXIT
# ============================================================

def exit_program():
    root.destroy()


# ============================================================
# SCROLLABLE MAIN WINDOW
# ============================================================

main_container = tk.Frame(
    root
)

main_container.pack(
    fill=tk.BOTH,
    expand=True
)

canvas = tk.Canvas(
    main_container
)

canvas.pack(
    side=tk.LEFT,
    fill=tk.BOTH,
    expand=True
)

vertical_scrollbar = tk.Scrollbar(
    main_container,
    orient=tk.VERTICAL,
    command=canvas.yview
)

vertical_scrollbar.pack(
    side=tk.RIGHT,
    fill=tk.Y
)

canvas.configure(
    yscrollcommand=vertical_scrollbar.set
)

content_frame = tk.Frame(
    canvas
)

canvas_window = canvas.create_window(
    (0, 0),
    window=content_frame,
    anchor="nw"
)


def update_scroll_region(
    event=None
):

    canvas.configure(
        scrollregion=canvas.bbox("all")
    )


content_frame.bind(
    "<Configure>",
    update_scroll_region
)


def resize_content(event):

    canvas.itemconfig(
        canvas_window,
        width=event.width
    )


canvas.bind(
    "<Configure>",
    resize_content
)


def mouse_wheel(event):

    canvas.yview_scroll(
        int(-1 * (event.delta / 120)),
        "units"
    )


canvas.bind(
    "<Enter>",
    lambda event:
    canvas.bind_all(
        "<MouseWheel>",
        mouse_wheel
    )
)

canvas.bind(
    "<Leave>",
    lambda event:
    canvas.unbind_all(
        "<MouseWheel>"
    )
)


# ============================================================
# MAIN TITLE
# ============================================================

tk.Label(
    content_frame,
    text="PERSONAL EXPENSE TRACKER",
    font=("Arial", 24, "bold")
).pack(
    pady=25
)

tk.Label(
    content_frame,
    text=(
        "Manage income, expenses, "
        "monthly/yearly records and reports"
    ),
    font=("Arial", 12)
).pack(
    pady=5
)


# ============================================================
# BUTTON FRAME
# ============================================================

button_frame = tk.Frame(
    content_frame
)

button_frame.pack(
    pady=25
)


# ============================================================
# MAIN BUTTONS
# ============================================================

buttons = [

    (
        "Add Transaction",
        add_new_transaction
    ),

    (
        "View Transactions",
        view_transactions
    ),

    (
        "Search Transaction",
        search_transaction
    ),

    (
        "Advanced Search",
        advanced_transaction_search
    ),

    (
        "Update Transaction",
        update_existing_transaction
    ),

    (
        "Delete Transaction",
        delete_transaction_menu
    ),

    (
        "Financial Summary",
        show_summary
    ),

    (
        "Financial Dashboard",
        financial_dashboard
    ),

    (
        "Monthly Report",
        monthly_report
    ),

    (
        "Category Report",
        category_report
    ),

    (
        "Add Monthly/Yearly Record",
        add_recurring_record_window
    ),

    (
        "View Monthly/Yearly Records",
        view_recurring_records
    ),

    (
        "Update Monthly/Yearly Record",
        update_recurring_record_window
    ),

    (
        "Delete Monthly/Yearly Records",
        delete_recurring_records
    ),

    (
        "Monthly/Yearly Report",
        recurring_report
    ),

    (
        "Yearly Comparison",
        yearly_comparison
    ),

    (
        "Export Transactions",
        export_transactions
    ),

    (
        "Export Monthly/Yearly",
        export_recurring_records
    ),

    (
        "Backup Database",
        backup_database
    ),

    (
        "Exit",
        exit_program
    )
]


# ============================================================
# CREATE BUTTONS
# ============================================================

for index, (
    text,
    command
) in enumerate(buttons):

    row = index // 2
    column = index % 2

    tk.Button(
        button_frame,
        text=text,
        width=30,
        height=2,
        command=command
    ).grid(
        row=row,
        column=column,
        padx=10,
        pady=8
    )


# ============================================================
# EXTRA SPACE
# ============================================================

tk.Label(
    content_frame,
    text="",
    height=3
).pack()


# ============================================================
# START GUI
# ============================================================

root.mainloop()