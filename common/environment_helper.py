import __builtin__
import os
import yaml


class EnvironmentHelper(object):

    @staticmethod
    def set_environment(logger_function):
        __builtin__.environment = None
        __builtin__.slack_token = None
        try:
            __builtin__.environment = os.environ['ENVIRONMENT']
            __builtin__.slack_token = os.environ['SLACK_TOKEN']
        except KeyError as e:
            logger_function("Must configure ENVIRONMENT variable and SLACK_TOKEN variable in your environment in order "
                            "for application to start")
            logger_function(e.message)
            exit()
        else:
            logger_function("Environment set to: " + __builtin__.environment)
            logger_function("Slack token set to: " + __builtin__.slack_token)

            # Use the environment variable from above to read yaml config file and set
            # global variable to the loaded file so tier specific information may be retrieved
            # by the various modules as needed.
            with open(os.path.abspath("config/environment.yml"), 'r') as yaml_file:
                __builtin__.environment_config = yaml.load(yaml_file)
