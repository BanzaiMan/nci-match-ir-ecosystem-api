import os
import logging
import __builtin__
import yaml

from accessors.ion_reporter_accessor import IonReporterAccessor
from accessors.sample_control_accessor import SampleControlAccessor
from celery import Celery
from common.vcf_processor import VcfFileProcessor
from common.bam_processor import BamFileProcessor
from accessors.s3_accessor import S3Accessor
from werkzeug.utils import secure_filename

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


# I don't think we will use this for sample control as our sample control creation of records are not done through
# the queueing system but directly on the database. However, I'll leave this for now.
@app.task
def put(put_message):
    logger.info("Creating item: " + str(put_message))
    SampleControlAccessor().put_item(put_message)


# Use for just updating the data in a record in the table
@app.task
def update(update_message):
    logger.info("Updating item: " + str(update_message))
    SampleControlAccessor().update(update_message)


@app.task
def update_ir(update_message):
    logger.info("Updating item: " + str(update_message))
    IonReporterAccessor().update(update_message)


# this is a special update in that it updates the database, process files, and stores them in s3. So think of this
# as updating both S3 and dynamodb.
@app.task
def process_ir_file(file_process_message):
    logger.info("Updating sample_controls table before processing file" + str(file_process_message))
    new_file_process_message = file_process_message.copy()
    # after running SampleControlAccessor().update(file_process_message), key 'molecular_id' will be removed from file_process_message
    # see sample_control_access.py line37
    SampleControlAccessor().update(file_process_message)

    # process vcf, dna_bam, or cdna_bam file
    updated_file_process_message = process_file_message(new_file_process_message)
    # TODO: I think a try except is more appropriate as the above failing is an error not a valid conditional path.
    if updated_file_process_message is not None:
        logger.info("Updating sample_controls table after processing file")
        SampleControlAccessor().update(updated_file_process_message)


# process vcf, bam files based on message dictionary key: vcf_name, dna_bam_name, or cdna_bam_name
def process_file_message(file_process_message):
    logger.info("Processing file message in function process_file_message()" + str(file_process_message))

    if 'vcf_name' in file_process_message and file_process_message['vcf_name'] is not None:
        logger.info("Processing VCF ")
        downloaded_file_path = S3Accessor().download(file_process_message['vcf_name'])
        new_file_path = VcfFileProcessor().vcf_to_tsv(downloaded_file_path)
        # TODO: Qing, not be overly critical, but naming this variable "key" doesn't make sense to me. Is there a reason why? I ask because the file names are not keys.
        key = 'tsv_name'
    elif 'dna_bam_name' in file_process_message and file_process_message['dna_bam_name'] is not None:
        logger.info("Processing DNA BAM ")
        downloaded_file_path = S3Accessor().download(file_process_message['dna_bam_name'])
        new_file_path = BamFileProcessor().bam_to_bai(downloaded_file_path)
        key = 'dna_bai_name'
    elif 'cdna_bam_name' in file_process_message and file_process_message['cdna_bam_name'] is not None:
        logger.info("Processing RNA BAM ")
        downloaded_file_path = S3Accessor().download(file_process_message['cdna_bam_name'])
        new_file_path = BamFileProcessor().bam_to_bai(downloaded_file_path)
        key = 'cdna_bai_name'
    else:
        logger.error("No file needs process for " + str(file_process_message))
        # TODO: Qing, should raise an error here not simply return none as this is a true error
        return None

    new_file_name = secure_filename(os.path.basename(new_file_path))
    new_file_s3_path = file_process_message['site'] + "/" + file_process_message['molecular_id'] + \
                       "/" + file_process_message['analysis_id'] + "/" + new_file_name
    S3Accessor().upload(downloaded_file_path, new_file_s3_path)
    file_process_message.update({key: new_file_s3_path})
    return file_process_message


@app.task
def delete(molecular_id):
    logger.info("Deleting sample control record with molecular id:" + str(molecular_id))
    SampleControlAccessor().delete_item(molecular_id)


@app.task
def delete_ir(ion_reporter_id):
    logger.info("Deleting ion reporter record with ion reporter id:" + str(ion_reporter_id))
    IonReporterAccessor().delete_item(ion_reporter_id)


@app.task
def batch_delete(query_parameters):
    logger.info("Deleting sample control records matching query:" + str(query_parameters))
    SampleControlAccessor().batch_delete(query_parameters)


@app.task
def batch_delete_ir(query_parameters):
    logger.info("Deleting ion reporter records matching query:" + str(query_parameters))
    IonReporterAccessor().batch_delete(query_parameters)