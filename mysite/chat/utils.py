import string
import random

def generate_group_name(size=10, chars=string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))
