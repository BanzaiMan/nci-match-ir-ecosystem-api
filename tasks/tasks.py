import os
import logging
from logging.config import fileConfig
import json
import ast
import __builtin__
import urllib
import requests
from collections import Mapping, Set, Sequence
from decimal import Decimal

from accessors.ion_reporter_accessor import IonReporterAccessor
from accessors.sample_control_accessor import SampleControlAccessor
from celery import Celery
from common.sequence_file_processor import SequenceFileProcessor
from accessors.s3_accessor import S3Accessor
from werkzeug.utils import secure_filename
from common.environment_helper import EnvironmentHelper
from resource_helpers.ped_match_bot import PedBot

# Logging functionality
fileConfig(os.path.abspath("config/logging_config.ini"))
logger = logging.getLogger(__name__)
EnvironmentHelper.set_environment(logger.info)

# Setting up the Celery broker but making sure to ensure environment variables are in place
try:
    BROKER__URL = 'sqs://%s:%s@' % (urllib.quote(os.environ['AWS_ACCESS_KEY_ID'], safe=''),
                                   urllib.quote(os.environ['AWS_SECRET_ACCESS_KEY'], safe=''))
except KeyError as e:
    logger.error("Setup your queue name by setting AWS_ACCESS_KEY_ID or AWS_SECRET_ACCESS_KEY variable: " + e.message)
    exit()
else:
    BROKER_TRANSPORT_OPTIONS = {
        'polling_interval': __builtin__.environment_config[__builtin__.environment]['polling_interval']
    }
    app = Celery('tasks', broker=BROKER__URL, broker_transport_options=BROKER_TRANSPORT_OPTIONS)
    app.conf.CELERY_ACCEPT_CONTENT = ['json']
    app.conf.CELERY_TASK_SERIALIZER = 'json'
    try:
        app.conf.CELERY_DEFAULT_QUEUE = os.environ['IR_QUEUE_NAME']
    except KeyError as e:
        try:
            app.conf.CELERY_DEFAULT_QUEUE = __builtin__.environment_config[__builtin__.environment]['ir_queue_name']
        except KeyError as e:
            logger.error("Need to setup your queue name by setting IR_QUEUE_NAME variable: " + e.message)
            exit()

    app.conf.CELERY_ENABLE_REMOTE_CONTROL = False

slack_channel_id = (__builtin__.environment_config[__builtin__.environment]['slack_channel_id'])


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
# molecular_id_type is 'sample_control' or 'patient'
def process_ir_file(file_process_message):

    new_file_process_message = file_process_message.copy()

    if file_process_message['molecular_id_type'] == 'sample_control':
        logger.info("Updating sample_controls table before processing file" + str(file_process_message))
       # new_file_process_message = file_process_message.copy()
        # after running SampleControlAccessor().update(file_process_message), key 'molecular_id' will be
        # removed from file_process_message. See sample_control_access.py line37
        SampleControlAccessor().update(file_process_message)

    try:
        # process vcf, dna_bam, or cdna_bam file
        updated_file_process_message = process_file_message(new_file_process_message)
    except Exception as ex:
        PedBot().send_message(channel_id=slack_channel_id, message="Cannot process file because: " + ex.message)
        logger.error("Cannot process file because: " + ex.message)
    else:
        if file_process_message['molecular_id_type']  == 'sample_control':
            logger.info("Updating sample_controls table after processing file")
            SampleControlAccessor().update(updated_file_process_message)
            return None
        else:
            logger.info("Passing processed file S3 path to patient ecosystem")
            logger.info("processed file for patient: " + str(updated_file_process_message))


# process vcf, bam files based on message dictionary key: vcf_name, dna_bam_name, or cdna_bam_name
def process_file_message(file_process_message):
    logger.debug("Processing file message in function process_file_message()" + str(file_process_message))
    unicode_free_dictionary = ast.literal_eval(json.dumps(file_process_message))
    logger.debug("After Removing unicode" + str(unicode_free_dictionary))

    try:
        if 'vcf_name' in unicode_free_dictionary and unicode_free_dictionary['vcf_name'] is not None:
            new_file_path, key, downloaded_file_path = process_vcf(unicode_free_dictionary)

        elif 'dna_bam_name' in unicode_free_dictionary and unicode_free_dictionary['dna_bam_name'] is not None:
            new_file_path, key, downloaded_file_path = process_bam(unicode_free_dictionary, 'dna')

        elif 'cdna_bam_name' in unicode_free_dictionary and unicode_free_dictionary['cdna_bam_name'] is not None:
            new_file_path, key, downloaded_file_path = process_bam(unicode_free_dictionary, 'cdna')

        else:
            logger.info("File does not require processing" + str(file_process_message))
            return unicode_free_dictionary

    except Exception as e:
        PedBot().send_message(channel_id=slack_channel_id, message="Cannot process file because: " + e.message)
        raise Exception(e.message)

    else:
        new_file_name = secure_filename(os.path.basename(new_file_path))
        new_file_s3_path = unicode_free_dictionary['ion_reporter_id'] + "/" + unicode_free_dictionary['molecular_id'] + \
                           "/" + unicode_free_dictionary['analysis_id'] + "/" + new_file_name
        try:
            S3Accessor().upload(downloaded_file_path, new_file_s3_path)
        except Exception as e:

            raise Exception(e.message)
        else:
            unicode_free_dictionary.update({key: new_file_s3_path})
            if key=='tsv_name':
                if unicode_free_dictionary['molecular_id_type']=='patient':
                    post_tsv_info(unicode_free_dictionary, new_file_name)
                # try:
                #   unicode_free_dictionary = process_rule_by_tsv(unicode_free_dictionary, new_file_name)
                # except Exception as e:
                #     raise Exception("Failed to read Rule Engine for " + new_file_name+ " , because: " + e.message)
            return unicode_free_dictionary


def process_vcf(dictionary):
    logger.info("Processing VCF ")
    try:
        downloaded_file_path = S3Accessor().download(dictionary['vcf_name'])
    except Exception as e:
        raise Exception("Failed to download vcf file from S3, because: " + e.message)
    else:
        try:
            new_file_path = SequenceFileProcessor().vcf_to_tsv(downloaded_file_path)
        except Exception as e:
            # TODO: Posting that a vcf to tsv failed by itself isn't enough information for us to fix the issue. We need the file full paths etc.
            PedBot().send_message(channel_id=slack_channel_id, message="VCF creation failed because: " + e.message)
            raise Exception("VCF creation failed because: " + e.message)
        else:
            key = 'tsv_name'
            return new_file_path, key, downloaded_file_path


def process_bam(dictionary, nucleic_acid_type):
    logger.info("Processing " + nucleic_acid_type + " BAM ")
    try:
        downloaded_file_path = S3Accessor().download(dictionary[nucleic_acid_type + '_bam_name'])
    except Exception as e:
        raise Exception("Failed to download " + nucleic_acid_type + " BAM file from S3, because: " + e.message)
    else:
        try:
            new_file_path = SequenceFileProcessor().bam_to_bai(downloaded_file_path)
        except Exception as e:
            # TODO: Posting that a bam to bai failed by itself isn't enough information for us to fix the issue. We need the file full paths etc.
            PedBot().send_message(channel_id=slack_channel_id, message="BAI creation failed because: " + e.message)
            raise Exception("BAI creation failed because: " + e.message)
        else:
            key = nucleic_acid_type + '_bai_name'
            return new_file_path, key, downloaded_file_path

def post_tsv_info(dictionary, tsv_file_name):

    logger.info("Posting tsv file name to Patient Ecosystem for " + dictionary['molecular_id'])
    patient_url = (__builtin__.environment_config[__builtin__.environment]['patient_endpoint']
           + __builtin__.environment_config[__builtin__.environment]['patient_post_path'])
    headers = {'Content-type': 'application/json'}
    content = {'tsv_file_name': tsv_file_name,
               'ion_reporter_id': dictionary['ion_reporter_id'],
                'molecular_id': dictionary['molecular_id'],
                'analysis_id': dictionary['analysis_id']}

    try:
        r = requests.post(patient_url, data=json.dumps(content), headers=headers)
    except Exception as e:
        # TODO: Posting that a vcf to tsv failed by itself isn't enough information for us to fix the issue. We need the file full paths etc.
        PedBot().send_message(channel_id=slack_channel_id, message="Failed to post tsv file name to Patient Ecosystem because: " + e.message)
        raise Exception("Failed to post tsv file name to Patient Ecosystem for " + dictionary['molecular_id'] + ", because: " + e.message)
    else:
        if r.status_code ==200:
            logger.info("Successfully post tsv file name to Patient Ecosystem for " + dictionary['molecular_id'])
        else:
            PedBot().send_message(channel_id=slack_channel_id,
                                  message="Failed to post tsv file name to Patient Ecosystem because: " + r.text)
            logger.debug("Failed to post tsv file name to Patient Ecosystem for " + dictionary['molecular_id'] + ", because:" + r.text)

# TODO: save varient report data to sample_controls table
# def process_rule_by_tsv(dictionary, tsv_file_name):
#     url = (__builtin__.environment_config[__builtin__.environment]['rule_endpoint']
#            + __builtin__.environment_config[__builtin__.environment]['rule_path'])
#
#     url = url + dictionary['control_type'] + "/" + dictionary['ion_reporter_id'] + "/" + dictionary['molecular_id'] \
#         + "/" + dictionary['analysis_id'] + "/" + tsv_file_name.split(".")[0] + "?format=tsv"
#
#     print "========================== rule_URL= " + str(url)
#     try:
#         headers = {'Content-type': 'application/json'}
#         rule_data = requests.post(url, data=json.dumps({}), headers=headers)
#     except Exception as e:
#         raise Exception("Failed to get rule engine data for " + tsv_file_name + ", because: " + e.message)
#     else:
#         print "========================== rule_data=" + str(rule_data.text)
#
#     return dictionary


def sanitize(data):
    """ Sanitizes an object so it can be updated to dynamodb (recursive) """
    if not data and isinstance(data, (basestring, Set)):
        new_data = None  # empty strings/sets are forbidden by dynamodb
    elif isinstance(data, (basestring, bool)):
        new_data = data  # important to handle these one before sequence and int!
    elif isinstance(data, Mapping):
        new_data = {key: sanitize(data[key]) for key in data}
    elif isinstance(data, Sequence):
        new_data = [sanitize(item) for item in data]
    elif isinstance(data, Set):
        new_data = {sanitize(item) for item in data}
    elif isinstance(data, (float, int, long, complex)):
        new_data = Decimal(str(data))
    else:
        new_data = data

    return new_data

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
