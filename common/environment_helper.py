import __builtin__
import os


class EnvironmentHelper(object):

    @staticmethod
    def set_environment(logger_function):
        __builtin__.environment = None
        try:
            __builtin__.environment = os.environ['ENVIRONMENT']
        except KeyError as e:
            logger_function("Must configure ENVIRONMENT variable in your environment in order for application to start")
            logger_function(e.message)
        else:
            logger_function("Environment set to: " + __builtin__.environment)
