import re

def validate_password(password):

    # Регулярное выражение для проверки пароля
    pattern = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$')

    if pattern.match(password):
        return password
    raise ValueError
