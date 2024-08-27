from . import db
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime

# IFRS-compliant Models
'''
Account:
Represents general ledger accounts (Assets, Liabilities, Equity, Revenue, Expenses).
Each account has a unique code, name, type, and balance.

'''
class Account(db.Model):
    __tablename__ = 'accounts'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    account_type = db.Column(db.String(50), nullable=False)  # e.g., Asset, Liability, Equity, Revenue, Expense
    code = db.Column(db.String(50), unique=True, nullable=False)  # Account code, e.g., "1001" for cash
    description = db.Column(db.Text)
    balance = db.Column(db.Float, default=0.0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    transactions = db.relationship('Transaction', backref='account', lazy=True)

    def __repr__(self):
        return f'<Account {self.name} ({self.code})>'


'''
Transaction:
Represents individual transactions (debit or credit) posted to accounts.
Each transaction is linked to an account.
'''
class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    transaction_type = db.Column(db.String(10), nullable=False)  # 'debit' or 'credit'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Transaction {self.id} - {self.transaction_type.capitalize()} {self.amount} on {self.date}>'

'''
JournalEntry and JournalEntryLine:
JournalEntry: Represents a complete journal entry, containing multiple lines (debits and credits).
JournalEntryLine: Represents each line in a journal entry, specifying the debit or credit amount for an account.
'''

class JournalEntry(db.Model):
    __tablename__ = 'journal_entries'

    id = db.Column(db.Integer, primary_key=True)
    entry_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    reference = db.Column(db.String(100), nullable=True)  # Reference to invoice, bill, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    lines = db.relationship('JournalEntryLine', backref='journal_entry', lazy=True)

    def __repr__(self):
        return f'<JournalEntry {self.id} on {self.entry_date}>'

class JournalEntryLine(db.Model):
    __tablename__ = 'journal_entry_lines'

    id = db.Column(db.Integer, primary_key=True)
    journal_entry_id = db.Column(db.Integer, db.ForeignKey('journal_entries.id'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    debit = db.Column(db.Float, default=0.0)
    credit = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<JournalEntryLine {self.id} - Debit: {self.debit} Credit: {self.credit}>'
'''
FinancialStatement and FinancialStatementItem:
FinancialStatement: Represents the entire financial statement (Balance Sheet, Income Statement) for a given period.
FinancialStatementItem: Represents individual line items in a financial statement, typically aggregated from the ledger.
'''
class FinancialStatement(db.Model):
    __tablename__ = 'financial_statements'

    id = db.Column(db.Integer, primary_key=True)
    statement_type = db.Column(db.String(50), nullable=False)  # e.g., "Balance Sheet", "Income Statement"
    period_start = db.Column(db.DateTime, nullable=False)
    period_end = db.Column(db.DateTime, nullable=False)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    items = db.relationship('FinancialStatementItem', backref='financial_statement', lazy=True)

    def __repr__(self):
        return f'<FinancialStatement {self.statement_type} for period {self.period_start} to {self.period_end}>'

class FinancialStatementItem(db.Model):
    __tablename__ = 'financial_statement_items'

    id = db.Column(db.Integer, primary_key=True)
    financial_statement_id = db.Column(db.Integer, db.ForeignKey('financial_statements.id'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<FinancialStatementItem {self.id} - Account: {self.account_id} Amount: {self.amount}>'

'''
Invoice and InvoiceLineItem:

Invoice: Represents an issued invoice, including client details, amount, and status.
InvoiceLineItem: Represents individual items in an invoice, including quantity, unit price, and total price.
'''
class Invoice(db.Model):
    __tablename__ = 'invoices'

    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    date_issued = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    due_date = db.Column(db.DateTime, nullable=False)
    client_name = db.Column(db.String(255), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='unpaid')  # e.g., unpaid, paid, overdue

    # Relationships
    line_items = db.relationship('InvoiceLineItem', backref='invoice', lazy=True)

    def __repr__(self):
        return f'<Invoice {self.invoice_number} - {self.client_name}>'

class InvoiceLineItem(db.Model):
    __tablename__ = 'invoice_line_items'

    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<InvoiceLineItem {self.id} - {self.description} x {self.quantity}>'


'''
IFRS Compliance: This model structure is designed to be general-purpose and adaptable. You should customize it further to ensure full compliance with specific IFRS standards applicable to your jurisdiction or industry.
Extensibility: You can expand these models to include more detailed features, such as tax handling, multi-currency transactions, or specific ledger accounts required under IFRS.
Validation and Constraints: You may need to add additional validation and constraints to ensure that the data entered into the system adheres to IFRS and other regulatory requirements.
This template serves as a starting point for building a robust accounting application that follows IFRS standards. You should tailor it further to meet the specific needs of your application and business requirements.
'''