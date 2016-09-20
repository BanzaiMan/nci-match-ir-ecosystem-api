import os
import logging
from logging.config import fileConfig
import json
import ast

from accessors.ion_reporter_accessor import IonReporterAccessor
from accessors.sample_control_accessor import SampleControlAccessor
from celery import Celery
from common.sequence_file_processor import SequenceFileProcessor
from accessors.s3_accessor import S3Accessor
from werkzeug.utils import secure_filename
from common.environment_helper import EnvironmentHelper

# Logging functionality
fileConfig(os.path.abspath("config/logging_config.ini"))
logger = logging.getLogger(__name__)

BROKER__URL = "sqs://" + os.environ['AWS_ACCESS_KEY_ID'] + ":" + os.environ['AWS_SECRET_ACCESS_KEY'] + "@"
app = Celery('tasks', broker=BROKER__URL)

EnvironmentHelper.set_environment(logger.info)


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
    # after running SampleControlAccessor().update(file_process_message), key 'molecular_id' will be
    # removed from file_process_message. See sample_control_access.py line37
    SampleControlAccessor().update(file_process_message)

    try:
        # process vcf, dna_bam, or cdna_bam file
        updated_file_process_message = process_file_message(new_file_process_message)
    except Exception as ex:
        logger.error("Cannot process file because: " + ex.message)
        raise
    else:
        logger.info("Updating sample_controls table after processing file")
        SampleControlAccessor().update(updated_file_process_message)


# process vcf, bam files based on message dictionary key: vcf_name, dna_bam_name, or cdna_bam_name
def process_file_message(file_process_message):
    logger.debug("Processing file message in function process_file_message()" + str(file_process_message))
    unicode_free_dictionary = ast.literal_eval(json.dumps(file_process_message))
    logger.debug("After Removing unicode" + str(unicode_free_dictionary))
    if 'vcf_name' in unicode_free_dictionary and unicode_free_dictionary['vcf_name'] is not None:
        logger.info("Processing VCF ")
        # TODO: Need to check for error
        downloaded_file_path = S3Accessor().download(unicode_free_dictionary['vcf_name'])
        try:
            new_file_path = SequenceFileProcessor().vcf_to_tsv(downloaded_file_path)
        except Exception as e:
            raise Exception("VCF creation failed because: " + e.message)
        else:
            key = 'tsv_name'
    elif 'dna_bam_name' in unicode_free_dictionary and unicode_free_dictionary['dna_bam_name'] is not None:
        logger.info("Processing DNA BAM ")
        downloaded_file_path = S3Accessor().download(unicode_free_dictionary['dna_bam_name'])
        try:
            new_file_path = SequenceFileProcessor().bam_to_bai(downloaded_file_path)
        except Exception as e:
            raise Exception("BAI creation failed because: " + e.message)
        else:
            key = 'dna_bai_name'
    elif 'cdna_bam_name' in unicode_free_dictionary and unicode_free_dictionary['cdna_bam_name'] is not None:
        logger.info("Processing RNA BAM ")
        downloaded_file_path = S3Accessor().download(unicode_free_dictionary['cdna_bam_name'])
        try:
            new_file_path = SequenceFileProcessor().bam_to_bai(downloaded_file_path)
        except Exception as e:
            raise Exception("BAI creation failed because: " + e.message)
        else:
            key = 'cdna_bai_name'
    else:
        logger.info("File does not require processing" + str(file_process_message))
        return unicode_free_dictionary

    new_file_name = secure_filename(os.path.basename(new_file_path))
    new_file_s3_path = unicode_free_dictionary['site'] + "/" + unicode_free_dictionary['molecular_id'] + \
                       "/" + unicode_free_dictionary['analysis_id'] + "/" + new_file_name
    S3Accessor().upload(downloaded_file_path, new_file_s3_path)
    unicode_free_dictionary.update({key: new_file_s3_path})
    return unicode_free_dictionary


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
