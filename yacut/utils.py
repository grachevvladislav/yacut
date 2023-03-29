import random
import string

from .models import URLMap


def get_unique_short_id():
    chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
    short = ''.join(random.choice(chars) for _ in range(6))
    while URLMap.query.filter_by(short=short).first() is not None:
        short = ''.join(random.choice(chars) for _ in range(6))
    return short
