import __builtin__
import os
import yaml


class EnvironmentHelper(object):
    """Method to set environment"""
    @staticmethod
    def set_environment(logger):
        logger.info("Checking if Environment and Slack Token variable loaded")
        try:
            __builtin__.environment
            __builtin__.slack_token
        except Exception:
            logger.info("Environment and Slack Token variable not yet loaded, now attempting to load")
            try:
                __builtin__.environment = os.environ['ENVIRONMENT']
                __builtin__.slack_token = os.environ['SLACK_TOKEN']

            except KeyError as e:
                logger.error("Must configure ENVIRONMENT variable and SLACK_TOKEN variable in your"
                             "environment in order for application to start")
                logger.error(e.message)
                exit()
            else:
                logger.info("Environment set to: " + __builtin__.environment)
                logger.info("Slack token set to: " + __builtin__.slack_token)

                # Use the environment variable from above to read yaml config file and set
                # global variable to the loaded file so tier specific information may be retrieved
                # by the various modules as needed.
                with open(os.path.abspath("config/environment.yml"), 'r') as yaml_file:
                    __builtin__.environment_config = yaml.load(yaml_file)
        else:
            logger.info("Environment and Slack Token variable already loaded. Skipping load.")

