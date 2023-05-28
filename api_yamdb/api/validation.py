import re

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator


def username_is_valid(username):
    valid_username = re.compile(r'^[\w.@+-]+\Z')
    try:
        RegexValidator(valid_username,
                       message='Enter a valid username.',
                       code='invalid')(username)
        return True
    except ValidationError:
        return False
