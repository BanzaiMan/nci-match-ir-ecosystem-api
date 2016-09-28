import __builtin__
import os
import yaml


class EnvironmentHelper(object):

    @staticmethod
    def set_environment(logger_function):
        __builtin__.environment = None
        try:
            __builtin__.environment = os.environ['ENVIRONMENT']
        except KeyError as e:
            logger_function("Must configure ENVIRONMENT variable in your environment in order for application to start")
            logger_function(e.message)
            exit()
        else:
            logger_function("Environment set to: " + __builtin__.environment)

            # Use the environment variable from above to read yaml config file and set
            # global variable to the loaded file so tier specific information may be retrieved
            # by the various modules as needed.
            with open(os.path.abspath("config/environment.yml"), 'r') as yaml_file:
                __builtin__.environment_config = yaml.load(yaml_file)
