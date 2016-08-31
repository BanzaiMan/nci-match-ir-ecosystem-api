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
    logger.info("Processing file: " + str(file_process_message))

    # TODO: Now that this is done, we can refactor to be DRY (Don't Repeat Yourself)
    if 'vcf_name' in file_process_message:
        logger.info("Processing VCF ")
        vcf_local_path = S3Accessor().download(file_process_message['vcf_name'])
        tsv_full_path = VcfFileProcessor().vcf_to_tsv(vcf_local_path)
        tsv_file_name = secure_filename(os.path.basename(tsv_full_path))
        tsv_s3_path = file_process_message['site'] + "/" + file_process_message['molecular_id'] + \
                      "/" + file_process_message['analysis_id'] + "/" + tsv_file_name
        S3Accessor().upload(tsv_full_path, tsv_s3_path)
        file_process_message.update({'tsv_name': tsv_s3_path})
    elif 'dna_bam_name' in file_process_message:
        logger.info("Processing DNA BAM ")
        dna_bam_local_path = S3Accessor().download(file_process_message['dna_bam_name'])
        dna_bai_full_path = BamFileProcessor().bam_to_bai(dna_bam_local_path)
        dna_bai_full_name = secure_filename(os.path.basename(dna_bai_full_path))
        dna_bai_s3_path = file_process_message['site'] + "/" + file_process_message['molecular_id'] + \
                          "/" + file_process_message['analysis_id'] + "/" + dna_bai_full_name
        S3Accessor().upload(dna_bai_full_path, dna_bai_s3_path)
        file_process_message.update({'dna_bai_name': dna_bai_s3_path})
    elif 'cdna_bam_name' in file_process_message:
        logger.info("Processing RNA BAM ")
        cdna_bam_local_path = S3Accessor().download(file_process_message['cdna_bam_name'])
        cdna_bai_full_path = BamFileProcessor().bam_to_bai(cdna_bam_local_path)
        cdna_bai_full_name = secure_filename(os.path.basename(cdna_bai_full_path))
        cdna_bai_s3_path = file_process_message['site'] + "/" + file_process_message['molecular_id'] + \
                           "/" + file_process_message['analysis_id'] + "/" + cdna_bai_full_name
        S3Accessor().upload(cdna_bai_full_path, cdna_bai_s3_path)
        file_process_message.update({'cdna_bai_name': cdna_bai_s3_path})

    # TODO: This works, but isn't really safe. We should save the data before processing then save the new information after the files are processed.
    SampleControlAccessor().update(file_process_message)


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