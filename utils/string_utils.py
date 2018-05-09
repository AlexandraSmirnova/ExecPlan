import random
import string


def get_random_string(count, digits=True):
    choice = string.ascii_uppercase + string.digits if digits else string.ascii_uppercase
    return ''.join(random.choice(choice) for _ in range(count))