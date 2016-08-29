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
    def generate_ion_reporter_id(length=5):
        logger = logging.getLogger(__name__)
        logger.debug("Generating ion reporter id")

        new_ion_reporter_id = 'IR_' + StringHelper.generate_random_string(length)

        logger.debug("New Ion Reporter Id: " + new_ion_reporter_id)
        return new_ion_reporter_id

    @staticmethod
    def generate_random_string(length=5):
        if not isinstance(length, int):
            raise ValueError("Invalid Input")

        if length < 1:
            raise ValueError("Invalid Input")

        logger = logging.getLogger(__name__)
        logger.debug("Generating random string for molecular id")
        return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(length))
