import string
import random


class StringHelper(object):

    @staticmethod
    def generate_molecular_id(length=5):
        return 'SC_' + StringHelper.generate_random_string(length)

    @staticmethod
    def generate_random_string(length=5):
        return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(length))
