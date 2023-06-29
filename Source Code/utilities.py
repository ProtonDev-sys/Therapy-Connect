import re


def is_strong_password(password) -> bool:
    # Check length of password
    if len(password) < 8:
        return False

    # Check for uppercase character
    if not re.search(r'[A-Z]', password):
        return False

    # Check for lowercase character
    if not re.search(r'[a-z]', password):
        return False

    # Check for digit
    if not re.search(r'\d', password):
        return False

    # Check for special character
    if not re.search(r'[!@#$%^&*()\[\]{};:\'",.<>/?\\|]', password):
        return False

    # Password passes all checks
    return True
