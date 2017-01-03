from flask_restful import Resource
from resource_helpers.abort_logger import AbortLogger
import logging
import urllib
import os

class Version(Resource):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get(self):
        try:
            page = urllib.urlopen(os.path.abspath("build_number.html")).read()
        except Exception as e:
            AbortLogger.log_and_abort(500, self.logger.error,
                                      "Failed to load build_number.html because: " + e.message)
        return page