import random
import string


def get_random_string(count):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(count))