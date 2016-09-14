import string
import random
import logging


class StringHelper(object):

    @staticmethod
    def generate_molecular_id(prefix, length=5):
        logger = logging.getLogger(__name__)
        logger.debug("Generating molecular id")

        if type(prefix) is str:
            new_id = prefix + StringHelper.generate_random_string(length)

            logger.debug("New molecular id: " + new_id)
            return new_id
        else:
            raise Exception('Prefix must be string.')

    @staticmethod
    def generate_random_string(length=5):
        if not isinstance(length, int):
            raise ValueError("Invalid Input")

        if length < 1:
            raise ValueError("Invalid Input")

        logger = logging.getLogger(__name__)
        logger.debug("Generating random string for id")
        return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(length))
