import logging
import __builtin__
from single_key_accessor import SingleKeyAccessor


class SampleControlAccessor(SingleKeyAccessor):

    def __init__(self):
        self.KEY = 'molecular_id'
        self.logger = logging.getLogger(__name__)
        self.logger.debug("SampleControlAccessor instantiated")
        self.logger.debug("__builtin__.environment: " + str(__builtin__.environment))
        self.logger.debug("__builtin__.environment_config: " + str(__builtin__.environment_config))
        SingleKeyAccessor.__init__(self, 'sample_controls', self.KEY)
