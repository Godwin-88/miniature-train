from flask import Blueprint, jsonify, request, abort, render_template
from . import db
from .models import Account, Transaction, JournalEntry, JournalEntryLine, FinancialStatement, FinancialStatementItem
from datetime import datetime

# Define a Blueprint
main = Blueprint('main', __name__)

# Home page route
@main.route('/')
def home():
    return "Welcome to the Accounting Management System Home Page"

# Favicon route (Optional)
@main.route('/favicon.ico')
def favicon():
    return "", 204

# Create a new account
@main.route('/accounts', methods=['POST'])
def create_account():
    data = request.get_json()

    if not data or 'name' not in data or 'account_type' not in data or 'code' not in data:
        abort(400, description="Missing required fields")

    new_account = Account(
        name=data['name'],
        account_type=data['account_type'],
        code=data['code'],
        description=data.get('description', '')
    )

    db.session.add(new_account)
    db.session.commit()

    return jsonify({'message': 'Account created successfully', 'account': new_account.id}), 201

# Get all accounts
@main.route('/accounts', methods=['GET'])
def get_accounts():
    accounts = Account.query.all()
    result = [
        {
            'id': account.id,
            'name': account.name,
            'account_type': account.account_type,
            'code': account.code,
            'balance': account.balance
        }
        for account in accounts
    ]
    return jsonify(result), 200

# Post a transaction
@main.route('/transactions', methods=['POST'])
def post_transaction():
    data = request.get_json()

    if not data or 'account_id' not in data or 'amount' not in data or 'transaction_type' not in data:
        abort(400, description="Missing required fields")

    account = db.session.get(Account, data['account_id'])  # Updated to use db.session.get

    if not account:
        abort(404, description="Account not found")

    new_transaction = Transaction(
        account_id=data['account_id'],
        amount=data['amount'],
        transaction_type=data['transaction_type'],
        description=data.get('description', '')
    )

    # Update account balance based on transaction type
    if data['transaction_type'] == 'debit':
        account.balance += data['amount']
    elif data['transaction_type'] == 'credit':
        account.balance -= data['amount']
    else:
        abort(400, description="Invalid transaction type")

    db.session.add(new_transaction)
    db.session.commit()

    return jsonify({'message': 'Transaction posted successfully', 'transaction': new_transaction.id}), 201

# Create a journal entry
@main.route('/journal_entries', methods=['POST'])
def create_journal_entry():
    data = request.get_json()

    if not data or 'description' not in data or 'lines' not in data:
        abort(400, description="Missing required fields")

    new_journal_entry = JournalEntry(
        description=data['description'],
        reference=data.get('reference', '')
    )
    db.session.add(new_journal_entry)
    db.session.commit()

    total_debit = 0
    total_credit = 0

    for line in data['lines']:
        account = db.session.get(Account, line['account_id'])  # Updated to use db.session.get

        if not account:
            abort(404, description="Account not found")

        debit = line.get('debit', 0)
        credit = line.get('credit', 0)

        new_line = JournalEntryLine(
            journal_entry_id=new_journal_entry.id,
            account_id=account.id,
            debit=debit,
            credit=credit
        )
        db.session.add(new_line)

        # Update account balance
        account.balance += (debit - credit)

        total_debit += debit
        total_credit += credit

    if total_debit != total_credit:
        db.session.rollback()
        abort(400, description="Total debit and credit amounts must be equal")

    db.session.commit()

    return jsonify({'message': 'Journal entry created successfully', 'journal_entry': new_journal_entry.id}), 201

# Generate a financial statement (e.g., Balance Sheet, Income Statement)
@main.route('/financial_statements', methods=['POST'])
def generate_financial_statement():
    data = request.get_json()

    if not data or 'statement_type' not in data or 'period_start' not in data or 'period_end' not in data:
        abort(400, description="Missing required fields")

    statement_type = data['statement_type']
    period_start = datetime.strptime(data['period_start'], '%Y-%m-%d')  # Convert string to datetime
    period_end = datetime.strptime(data['period_end'], '%Y-%m-%d')  # Convert string to datetime

    new_statement = FinancialStatement(
        statement_type=statement_type,
        period_start=period_start,
        period_end=period_end
    )
    db.session.add(new_statement)
    db.session.commit()

    # Generate financial statement items based on the statement type
    accounts = Account.query.all()
    for account in accounts:
        if statement_type == 'Balance Sheet' and account.account_type in ['Asset', 'Liability', 'Equity']:
            amount = account.balance
        elif statement_type == 'Income Statement' and account.account_type in ['Revenue', 'Expense']:
            amount = account.balance
        else:
            continue

        new_item = FinancialStatementItem(
            financial_statement_id=new_statement.id,
            account_id=account.id,
            amount=amount
        )
        db.session.add(new_item)

    db.session.commit()

    return jsonify({'message': f'{statement_type} generated successfully', 'financial_statement': new_statement.id}), 201

# Get a financial statement by ID
@main.route('/financial_statements/<int:id>', methods=['GET'])
def get_financial_statement(id):
    statement = db.session.get(FinancialStatement, id)  # Updated to use db.session.get

    if not statement:
        abort(404, description="Financial statement not found")

    items = FinancialStatementItem.query.filter_by(financial_statement_id=id).all()

    result = {
        'id': statement.id,
        'statement_type': statement.statement_type,
        'period_start': statement.period_start,
        'period_end': statement.period_end,
        'items': [
            {
                'account_id': item.account_id,
                'amount': item.amount
            } for item in items
        ]
    }

    return jsonify(result), 200

