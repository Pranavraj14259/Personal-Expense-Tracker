from transaction import Transaction

from database import (
    add_transaction,
    get_all_transactions,
    find_transaction,
    update_transaction,
    delete_transaction,
    delete_all_transactions,
    get_summary
)


# ============================================================
# VALIDATION FUNCTIONS
# ============================================================

def get_valid_amount():
    while True:
        try:
            amount = float(
                input("Enter amount: ").strip()
            )

            if amount <= 0:
                print("Amount must be greater than 0.")
                continue

            return amount

        except ValueError:
            print("Please enter a valid amount.")


def get_transaction_type():
    while True:
        transaction_type = (
            input(
                "Enter type (Income/Expense): "
            )
            .strip()
            .capitalize()
        )

        if transaction_type in ["Income", "Expense"]:
            return transaction_type

        print(
            "Please enter either Income or Expense."
        )


# ============================================================
# ADD TRANSACTION
# ============================================================

def add_new_transaction():

    print("\n======================================")
    print("          ADD TRANSACTION")
    print("======================================")

    date = input(
        "Enter date (DD-MM-YYYY): "
    ).strip()

    description = input(
        "Enter description: "
    ).strip()

    category = input(
        "Enter category: "
    ).strip()

    amount = get_valid_amount()

    transaction_type = get_transaction_type()

    payment_method = input(
        "Enter payment method: "
    ).strip()

    transaction = Transaction(
        None,
        date,
        description,
        category,
        amount,
        transaction_type,
        payment_method
    )

    add_transaction(
        transaction.to_dict()
    )

    print(
        "\nTransaction added successfully!"
    )


# ============================================================
# VIEW TRANSACTIONS
# ============================================================

def view_transactions():

    transactions = get_all_transactions()

    if not transactions:
        print("\nNo transactions found.")
        return

    print("\n======================================")
    print("         ALL TRANSACTIONS")
    print("======================================")

    for transaction in transactions:

        print(
            f"Transaction ID : "
            f"{transaction['transaction_id']}"
        )

        print(
            f"Date           : "
            f"{transaction['date']}"
        )

        print(
            f"Description    : "
            f"{transaction['description']}"
        )

        print(
            f"Category       : "
            f"{transaction['category']}"
        )

        print(
            f"Amount         : "
            f"₹{transaction['amount']:.2f}"
        )

        print(
            f"Type           : "
            f"{transaction['transaction_type']}"
        )

        print(
            f"Payment Method : "
            f"{transaction['payment_method']}"
        )

        print(
            "--------------------------------------"
        )


# ============================================================
# SEARCH TRANSACTION
# ============================================================

def search_transaction():

    try:
        transaction_id = int(
            input(
                "Enter transaction ID: "
            ).strip()
        )

    except ValueError:
        print(
            "Please enter a valid transaction ID."
        )
        return

    transaction = find_transaction(
        transaction_id
    )

    if transaction is None:

        print(
            "\nTransaction not found."
        )

        return

    print("\n======================================")
    print("         TRANSACTION DETAILS")
    print("======================================")

    print(
        f"Transaction ID : "
        f"{transaction['transaction_id']}"
    )

    print(
        f"Date           : "
        f"{transaction['date']}"
    )

    print(
        f"Description    : "
        f"{transaction['description']}"
    )

    print(
        f"Category       : "
        f"{transaction['category']}"
    )

    print(
        f"Amount         : "
        f"₹{transaction['amount']:.2f}"
    )

    print(
        f"Type           : "
        f"{transaction['transaction_type']}"
    )

    print(
        f"Payment Method : "
        f"{transaction['payment_method']}"
    )


# ============================================================
# UPDATE TRANSACTION
# ============================================================

def update_existing_transaction():

    try:
        transaction_id = int(
            input(
                "Enter transaction ID to update: "
            ).strip()
        )

    except ValueError:

        print(
            "Please enter a valid transaction ID."
        )

        return

    existing = find_transaction(
        transaction_id
    )

    if existing is None:

        print(
            "\nTransaction not found."
        )

        return

    print("\nEnter new information:")

    date = input(
        "Enter new date (DD-MM-YYYY): "
    ).strip()

    description = input(
        "Enter new description: "
    ).strip()

    category = input(
        "Enter new category: "
    ).strip()

    amount = get_valid_amount()

    transaction_type = get_transaction_type()

    payment_method = input(
        "Enter new payment method: "
    ).strip()

    transaction = Transaction(
        transaction_id,
        date,
        description,
        category,
        amount,
        transaction_type,
        payment_method
    )

    success = update_transaction(
        transaction.to_dict()
    )

    if success:

        print(
            "\nTransaction updated successfully!"
        )

    else:

        print(
            "\nTransaction could not be updated."
        )


# ============================================================
# DELETE TRANSACTION
# ============================================================

def delete_transaction_menu():

    print("\n======================================")
    print("          DELETE TRANSACTION")
    print("======================================")

    print("1. Delete One Transaction")
    print("2. Delete All Transactions")
    print("3. Cancel")

    choice = input(
        "Enter your choice: "
    ).strip()

    # --------------------------------------------------------
    # DELETE ONE
    # --------------------------------------------------------

    if choice == "1":

        try:
            transaction_id = int(
                input(
                    "Enter transaction ID to delete: "
                ).strip()
            )

        except ValueError:

            print(
                "Please enter a valid transaction ID."
            )

            return

        transaction = find_transaction(
            transaction_id
        )

        if transaction is None:

            print(
                "\nTransaction not found."
            )

            return

        print(
            f"\nDescription: "
            f"{transaction['description']}"
        )

        print(
            f"Amount: "
            f"₹{transaction['amount']:.2f}"
        )

        confirmation = input(
            "Are you sure? Type yes to continue: "
        ).strip().lower()

        if confirmation == "yes":

            success = delete_transaction(
                transaction_id
            )

            if success:

                print(
                    "\nTransaction deleted successfully!"
                )

            else:

                print(
                    "\nTransaction could not be deleted."
                )

        else:

            print(
                "\nDelete operation cancelled."
            )

    # --------------------------------------------------------
    # DELETE ALL
    # --------------------------------------------------------

    elif choice == "2":

        transactions = get_all_transactions()

        total = len(transactions)

        if total == 0:

            print(
                "\nThere are no transactions."
            )

            return

        confirmation = input(
            f"\nThis will delete ALL {total} "
            "transactions.\n"
            "Type yes to continue: "
        ).strip().lower()

        if confirmation == "yes":

            deleted = delete_all_transactions()

            print(
                f"\n{deleted} transactions "
                "deleted successfully!"
            )

        else:

            print(
                "\nDelete operation cancelled."
            )

    elif choice == "3":

        print(
            "\nDelete operation cancelled."
        )

    else:

        print(
            "\nInvalid choice."
        )


# ============================================================
# FINANCIAL SUMMARY
# ============================================================

def show_summary():

    summary = get_summary()

    print("\n======================================")
    print("         FINANCIAL SUMMARY")
    print("======================================")

    print(
        f"Total Income   : "
        f"₹{summary['total_income']:.2f}"
    )

    print(
        f"Total Expenses : "
        f"₹{summary['total_expenses']:.2f}"
    )

    print(
        f"Balance        : "
        f"₹{summary['balance']:.2f}"
    )

    print(
        "======================================"
    )


# ============================================================
# MAIN MENU
# ============================================================

from gui import root


if __name__ == "__main__":
    root.mainloop()
while True:

    print("\n======================================")
    print("         PERSONAL EXPENSE TRACKER")
    print("======================================")

    print("1. Add Transaction")
    print("2. View Transactions")
    print("3. Search Transaction")
    print("4. Update Transaction")
    print("5. Delete Transaction")
    print("6. Financial Summary")
    print("7. Exit")

    choice = input(
        "\nEnter your choice: "
    ).strip()

    if choice == "1":

        add_new_transaction()

    elif choice == "2":

        view_transactions()

    elif choice == "3":

        search_transaction()

    elif choice == "4":

        update_existing_transaction()

    elif choice == "5":

        delete_transaction_menu()

    elif choice == "6":

        show_summary()

    elif choice == "7":

        print(
            "\nThank you for using "
            "Personal Expense Tracker!"
        )

        break

    else:

        print(
            "\nInvalid choice. "
            "Please enter a number from 1 to 7."
        )