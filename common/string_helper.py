import string
import random
import logging


class StringHelper(object):

    @staticmethod
    def generate_molecular_id(length=5):
        logger = logging.getLogger(__name__)
        logger.debug("Generating molecular id")

        new_molecular_id = 'SC_' + StringHelper.generate_random_string(length)

        logger.debug("New Molecular Id: " + new_molecular_id)
        return new_molecular_id

    @staticmethod
    def generate_random_string(length=5):
        logger = logging.getLogger(__name__)
        logger.debug("Generating random string for molecular id")
        return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(length))
