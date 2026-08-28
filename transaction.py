class Transaction:
    def __init__(
        self,
        transaction_id,
        date,
        description,
        category,
        amount,
        currency,
        transaction_type,
        payment_method
    ):
        self.transaction_id = transaction_id
        self.date = date
        self.description = description
        self.category = category
        self.amount = amount
        self.currency = currency
        self.transaction_type = transaction_type
        self.payment_method = payment_method

    def to_dict(self):
        return {
            "transaction_id": self.transaction_id,
            "date": self.date,
            "description": self.description,
            "category": self.category,
            "amount": self.amount,
            "currency": self.currency,
            "transaction_type": self.transaction_type,
            "payment_method": self.payment_method
        }

    def is_income(self):
        return self.transaction_type == "Income"

    def is_expense(self):
        return self.transaction_type == "Expense"


class RecurringRecord:
    def __init__(
        self,
        record_id,
        description,
        category,
        amount,
        currency,
        record_type,
        frequency,
        start_year
    ):
        self.record_id = record_id
        self.description = description
        self.category = category
        self.amount = amount
        self.currency = currency
        self.record_type = record_type
        self.frequency = frequency
        self.start_year = start_year

    def to_dict(self):
        return {
            "record_id": self.record_id,
            "description": self.description,
            "category": self.category,
            "amount": self.amount,
            "currency": self.currency,
            "record_type": self.record_type,
            "frequency": self.frequency,
            "start_year": self.start_year
        }

    def is_income(self):
        return self.record_type == "Income"

    def is_expense(self):
        return self.record_type == "Expense"

    def is_monthly(self):
        return self.frequency == "Monthly"

    def is_yearly(self):
        return self.frequency == "Yearly"