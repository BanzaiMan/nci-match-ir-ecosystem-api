import os
import logging
import __builtin__
import yaml

from accessors.sample_control_accessor import SampleControlAccessor
from celery import Celery

# Logging functionality
logger = logging.getLogger(__name__)

BROKER__URL = "sqs://" + os.environ['AWS_ACCESS_KEY_ID'] + ":" + os.environ['AWS_SECRET_ACCESS_KEY'] + "@"
app = Celery('tasks', broker=BROKER__URL)

try:
    __builtin__.environment = os.environ['ENVIRONMENT']

except KeyError, e:
    logger.error("Must configure ENVIRONMENT variable in your environment in order for application to start")
    logger.error(e.message)

logger.info("Environment set to: " + __builtin__.environment)

# Use the environment variable from above to read yaml config file set global variable
with open("config/environment.yml", 'r') as yaml_file:
    __builtin__.environment_config = yaml.load(yaml_file)


@app.task
def put(put_message):
    logger.info(put_message)
    SampleControlAccessor().put_item(put_message)
    return "You are putting an item"


@app.task
def update(update_message):
    logger.info(update_message)
    SampleControlAccessor().update(update_message)
    return "Done updating an item"


@app.task
def ir_file(file_process_message):
    logger.info(file_process_message)
    # TODO: process vcf and create tsv
    # TODO: add tsv path to update dictionary

    SampleControlAccessor().update(file_process_message)
    return "VCF written"

