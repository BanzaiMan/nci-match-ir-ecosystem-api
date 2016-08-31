import string
import random
import logging


class StringHelper(object):

    @staticmethod
    def generate_molecular_id(length=5):
        return StringHelper.__generate_id(length, "SC_", "sample_control")

    @staticmethod
    def generate_ion_reporter_id(length=5):
        return StringHelper.__generate_id(length, "IR_", "ion_reporter")

    @staticmethod
    def __generate_id(length, prefix, description):
        logger = logging.getLogger(__name__)
        logger.debug("Generating " + description + " id")

        new_id = prefix + StringHelper.generate_random_string(length)

        logger.debug("New " + description + ": " + new_id)
        return new_id

    @staticmethod
    def generate_random_string(length=5):
        if not isinstance(length, int):
            raise ValueError("Invalid Input")

        if length < 1:
            raise ValueError("Invalid Input")

        logger = logging.getLogger(__name__)
        logger.debug("Generating random string for molecular id")
        return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(length))
