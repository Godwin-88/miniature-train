import re
from datetime import datetime, timezone
from flask import jsonify

def validate_email(email):
    """
    Validates an email address using a regex pattern.
    Returns True if the email is valid, False otherwise.
    """
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None

def format_datetime(value, format='%Y-%m-%d %H:%M:%S'):
    """
    Formats a datetime object into a string.
    Default format is 'YYYY-MM-DD HH:MM:SS'.
    If the value is not a datetime object, it attempts to parse it.
    """
    if value is None:
        return None
    if isinstance(value, str):
        try:
            value = datetime.strptime(value, format)
        except (ValueError, TypeError):
            return None
    return value.strftime(format)

def parse_datetime(value, format='%Y-%m-%d %H:%M:%S'):
    """
    Parses a string into a datetime object.
    Default format is 'YYYY-MM-DD HH:MM:SS'.
    """
    try:
        return datetime.strptime(value, format)
    except (ValueError, TypeError):
        return None

def response_with(data=None, message="", success=True, status_code=200):
    """
    Utility function to standardize API responses.
    Returns a JSON response with a given structure.
    """
    response = {
        "success": success,
        "message": message,
        "data": data
    }
    return jsonify(response), status_code

def is_valid_currency_code(code):
    """
    Validates if the given code is a valid ISO 4217 currency code.
    """
    valid_currency_codes = ["USD", "EUR", "GBP", "JPY", "CAD", "AUD", "CHF", "CNY", "SEK", "NZD"]
    return code.upper() in valid_currency_codes

def generate_account_code(account_name):
    """
    Generates a simple account code based on the account name.
    This is a placeholder function and should be adjusted based on specific needs.
    """
    prefix = account_name[:3].upper()
    timestamp = datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')
    return f"{prefix}{timestamp}"

def convert_currency(amount, from_currency, to_currency, exchange_rate):
    """
    Converts an amount from one currency to another using the given exchange rate.
    """
    if from_currency == to_currency:
        return amount
    return round(amount * exchange_rate, 2)

'''
Explanation of the Utility Functions:
validate_email(email):

Uses a regular expression to validate an email address. This function returns True if the email is valid and False otherwise.
format_datetime(value, format='%Y-%m-%d %H:%M:%S'):

Converts a datetime object into a formatted string. You can adjust the format by passing a different format string.
parse_datetime(value, format='%Y-%m-%d %H:%M:%S'):

Parses a string into a datetime object using the provided format. If the string is invalid, it returns None.
response_with(data=None, message="", success=True, status_code=200):

A utility function to standardize API responses in your Flask application. This function returns a JSON response with a consistent structure.
is_valid_currency_code(code):

Checks if a given currency code is valid according to the ISO 4217 standard. This is a simplified list of common currency codes and can be expanded as needed.
generate_account_code(account_name):

Generates a simple, unique account code based on the account name and the current timestamp. This function can be customized to fit your specific needs for account code generation.
convert_currency(amount, from_currency, to_currency, exchange_rate):

Converts an amount from one currency to another using a given exchange rate. If the source and destination currencies are the same, it simply returns the original amount.
Usage in Your Application:
You can use these utility functions throughout your Flask application. For example:

Validation: Use validate_email when handling user input to ensure that email addresses are valid.
Datetime Formatting: Use format_datetime and parse_datetime to handle datetime conversions when interacting with your database or APIs.
API Responses: Use response_with to standardize the JSON responses returned by your API endpoints.
Currency Conversion: Use convert_currency to handle financial calculations involving different currencies.
Expanding utils.py
As your application grows, you might find the need to add more utility functions to utils.py. Keep this file organized by grouping related functions together and adding comments or docstrings to explain their purpose. This will make it easier to maintain and extend the functionality of your application.
'''