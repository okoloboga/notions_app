import re


def validate_password(password: str) -> str:
    """
    Validates a given password.

    A password should have at least 8 characters, one uppercase letter, one lowercase letter, one number and one special symbol.

    Args:
        password (str): The password to validate.

    Returns:
        str: The validated password if it is valid.

    Raises:
        ValueError: If the password is invalid.
    """

    pattern = re.compile(
        r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
    )

    if pattern.match(password):
        return password
    raise ValueError
