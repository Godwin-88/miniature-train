from .models import db, Account, Transaction, JournalEntry, JournalEntryLine, FinancialStatement, FinancialStatementItem
from .utils import convert_currency, generate_account_code, format_datetime
from datetime import datetime

def create_account(name, account_type, initial_balance=0.0, description=""):
    """
    Creates a new account in the system.
    """
    account_code = generate_account_code(name)
    new_account = Account(
        name=name,
        account_type=account_type,
        code=account_code,
        balance=initial_balance,
        description=description
    )
    db.session.add(new_account)
    db.session.commit()
    return new_account

def post_transaction(account_id, amount, transaction_type, description=""):
    """
    Posts a transaction (debit or credit) to an account.
    Updates the account balance accordingly.
    """
    account = db.session.get(Account, account_id)  # Updated to use db.session.get
    if not account:
        raise ValueError("Account not found")

    if transaction_type == 'debit':
        account.balance += amount
    elif transaction_type == 'credit':
        account.balance -= amount
    else:
        raise ValueError("Invalid transaction type")

    new_transaction = Transaction(
        account_id=account.id,
        amount=amount,
        transaction_type=transaction_type,
        description=description
    )
    db.session.add(new_transaction)
    db.session.commit()
    return new_transaction

def create_journal_entry(description, lines):
    total_debit = sum(line['debit'] for line in lines)
    total_credit = sum(line['credit'] for line in lines)

    if total_debit != total_credit:
        raise ValueError("Total debits must equal total credits")

    journal_entry = JournalEntry(description=description)
    db.session.add(journal_entry)
    db.session.commit()

    for line in lines:
        account = Account.query.get(line['account_id'])
        if not account:
            raise ValueError(f"Account ID {line['account_id']} not found")

        journal_line = JournalEntryLine(
            journal_entry_id=journal_entry.id,
            account_id=account.id,
            debit=line.get('debit', 0.0),
            credit=line.get('credit', 0.0)
        )

        # Update account balance correctly
        account.balance += line.get('debit', 0.0) - line.get('credit', 0.0)
        db.session.add(journal_line)

    db.session.commit()
    return journal_entry

def generate_financial_statement(statement_type, period_start, period_end):
    financial_statement = FinancialStatement(
        statement_type=statement_type,
        period_start=period_start,  # Pass datetime objects directly
        period_end=period_end        # Pass datetime objects directly
    )
    db.session.add(financial_statement)
    db.session.commit()

    accounts = Account.query.all()
    for account in accounts:
        if statement_type == 'Balance Sheet' and account.account_type in ['Asset', 'Liability', 'Equity']:
            amount = account.balance
        elif statement_type == 'Income Statement' and account.account_type in ['Revenue', 'Expense']:
            amount = account.balance
        else:
            continue

        statement_item = FinancialStatementItem(
            financial_statement_id=financial_statement.id,
            account_id=account.id,
            amount=amount
        )
        db.session.add(statement_item)

    db.session.commit()
    return financial_statement

def convert_and_post_transaction(account_id, amount, from_currency, to_currency, exchange_rate, transaction_type, description=""):
    """
    Converts an amount from one currency to another and posts the transaction.
    """
    converted_amount = convert_currency(amount, from_currency, to_currency, exchange_rate)
    return post_transaction(account_id, converted_amount, transaction_type, description)

'''

The services.py file typically contains business logic that interacts with your models and helps maintain clean separation between your route handlers and your core application logic. In the context of an accounting system that follows IFRS standards, services.py might include functions for handling common tasks such as creating journal entries, posting transactions, generating financial statements, and more.
Explanation of the Service Functions:
create_account(name, account_type, initial_balance=0.0, description=""):

Creates a new account with the provided name, type (e.g., Asset, Liability), and an optional initial balance.
Uses a utility function to generate a unique account code.
post_transaction(account_id, amount, transaction_type, description=""):

Posts a debit or credit transaction to the specified account.
Updates the account balance based on the transaction type.
create_journal_entry(description, lines):

Creates a journal entry with multiple lines, each representing a debit or credit to an account.
Ensures that the total debits equal the total credits, adhering to the double-entry accounting principle.
generate_financial_statement(statement_type, period_start, period_end):

Generates a financial statement, such as a Balance Sheet or Income Statement, for the specified period.
Aggregates account balances based on their types (e.g., Assets, Liabilities for Balance Sheet).
convert_and_post_transaction(account_id, amount, from_currency, to_currency, exchange_rate, transaction_type, description=""):

Converts an amount from one currency to another using the specified exchange rate and then posts the transaction.
This function is useful for handling multi-currency transactions, which are common in international accounting.
Using These Services in Your Routes:
In your routes.py or wherever you're handling API requests, you can use these service functions to process incoming data and perform the required actions. This keeps your route handlers clean and focused on handling HTTP requests and responses, while the business logic is encapsulated in the service layer.
'''