import __builtin__
import os
import yaml


class EnvironmentHelper(object):

    # TODO: Waleed this can be greatly simplified. Notice that  line  27 and 42 are identical. Also line30 -36 is almost the same as 13 throgugh 21. Any time you see a repetive pattern in code it typically means the code can be greatly simplfied and reduced
    @staticmethod
    def set_environment(logger_function):
        __builtin__.environment = None
        __builtin__.slack_token = None
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

        try:
            __builtin__.slack_token = os.environ['SLACK_TOKEN']
        except KeyError as e:
            logger_function("Must configure SLACK_TOKEN variable in your environment in order for application to start")
            logger_function(e.message)
        else:
            logger_function("Slack token set to: " + __builtin__.slack_token)

            # Use the environment variable from above to read yaml config file and set
            # global variable to the loaded file so tier specific information may be retrieved
            # by the various modules as needed.

            with open(os.path.abspath("config/environment.yml"), 'r') as yaml_file:
                __builtin__.environment_config = yaml.load(yaml_file)
