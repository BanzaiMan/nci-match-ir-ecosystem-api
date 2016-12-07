import __builtin__
import ast
import json
import logging
import os
import urllib
import inspect
import datetime
import requests

from logging.config import fileConfig
from string import Template
from celery import Celery
from werkzeug.utils import secure_filename

from accessors.ion_reporter_accessor import IonReporterAccessor
from accessors.s3_accessor import S3Accessor
from accessors.sample_control_accessor import SampleControlAccessor
from common.environment_helper import EnvironmentHelper
from common.ped_match_bot import PedMatchBot
from common.sequence_file_processor import SequenceFileProcessor

# Logging functionality
fileConfig(os.path.abspath("config/logging_config.ini"))
logger = logging.getLogger(__name__)
EnvironmentHelper.set_environment(logger)

# Setting up the Celery broker but making sure to ensure environment variables are in place
try:
    BROKER__URL = 'sqs://%s:%s@' % (urllib.quote(os.environ['AWS_ACCESS_KEY_ID'], safe=''),
                                   urllib.quote(os.environ['AWS_SECRET_ACCESS_KEY'], safe=''))
except KeyError as e:
    logger.error("Setup your queue name by setting AWS_ACCESS_KEY_ID or AWS_SECRET_ACCESS_KEY variable: " + e.message)
    exit()
else:
    BROKER_TRANSPORT_OPTIONS = {
        'polling_interval': __builtin__.environment_config[__builtin__.environment]['polling_interval'],
        'visibility_timeout': __builtin__.environment_config[__builtin__.environment]['visibility_timeout']
    }
    app = Celery('tasks', broker=BROKER__URL, broker_transport_options=BROKER_TRANSPORT_OPTIONS)
    app.conf.CELERY_ACCEPT_CONTENT = ['json']
    app.conf.CELERY_TASK_SERIALIZER = 'json'
    app.conf.CELERYD_PREFETCH_MULTIPLIER = 1
    try:
        app.conf.CELERY_DEFAULT_QUEUE = os.environ['IR_QUEUE_NAME']
    except KeyError as e:
        try:
            app.conf.CELERY_DEFAULT_QUEUE = __builtin__.environment_config[__builtin__.environment]['ir_queue_name']
        except KeyError as e:
            logger.error("Need to setup your queue name by setting IR_QUEUE_NAME variable: " + e.message)
            exit()

    app.conf.CELERY_ENABLE_REMOTE_CONTROL = False
    queue_name = app.conf.CELERY_DEFAULT_QUEUE
    dlx_queue = (queue_name + "_dlx")

MESSAGE_SERVICE_FAILURE = Template("Failure reaching: $service_name; \n S3 Path: $s3_path \n Service URL: $path \n Error "
                                   "Message: $message")
MESSAGE_CONVERSION_FAILURE = Template("Failure creating $conversion_type; \n File S3 Path: $s3_path \n Local Path: $path \n"
                                      "Error Message: $message")

def accessor_task(message, action, task, stack):
    logger.info(str(action) + " initiated for: " + str(message))
    try:
        action(message)
    except Exception as e:
        PedMatchBot.return_slack_message_and_retry(queue_name, message, e.message, stack, task, logger, dlx_queue)


@app.task
def put(put_message):
    stack = inspect.stack()
    action = SampleControlAccessor().put_item
    accessor_task(put_message, action, put, stack)

# Use for just updating the data in a record in the table
@app.task
def update(update_message):
    stack = inspect.stack()
    action = SampleControlAccessor().update
    accessor_task(update_message, action, update, stack)

@app.task
def update_ir(update_message):
    stack = inspect.stack()
    action = IonReporterAccessor().update
    accessor_task(update_message, action, update_ir, stack)


@app.task
def delete(molecular_id):
    stack = inspect.stack()
    action = SampleControlAccessor().delete_item
    accessor_task(molecular_id, action, delete, stack)


@app.task
def delete_ir(ion_reporter_id):
    stack = inspect.stack()
    action = IonReporterAccessor().delete_item
    accessor_task(ion_reporter_id, action, delete_ir, stack)


@app.task
def batch_delete(query_parameters):
    stack = inspect.stack()
    action = SampleControlAccessor().batch_delete
    accessor_task(query_parameters, action, batch_delete, stack)


@app.task
def batch_delete_ir(query_parameters):
    stack = inspect.stack()
    action = IonReporterAccessor().batch_delete
    accessor_task(query_parameters, action, batch_delete_ir, stack)

# this is a special update in that it updates the database, process files, and stores them in s3. So think of this
# as updating both S3 and dynamodb.
@app.task
def process_ir_file(file_process_message):
    new_file_process_message = file_process_message.copy()

    if new_file_process_message['molecular_id'] .startswith('SC_'):
        logger.info("Updating sample_controls table before processing file" + str(new_file_process_message))
        # after running SampleControlAccessor().update(file_process_message), key 'molecular_id' will be
        # removed from file_process_message. See sample_control_access.py line37
        SampleControlAccessor().update(file_process_message)

    if any(key in new_file_process_message for key in ('vcf_name', 'dna_bam_name', 'cdna_bam_name','qc_name')):
        try:
            # process vcf, dna_bam, or cdna_bam file
            updated_file_process_message = process_file_message(new_file_process_message)

        except Exception as e:
            stack = inspect.stack()
            PedMatchBot.return_slack_message_and_retry(queue_name, new_file_process_message, e.message, stack,
                                                       process_ir_file, logger, dlx_queue)
        else:
            if new_file_process_message['molecular_id'].startswith('SC_'):
                logger.info("Updating sample_controls table after processing file.")
                SampleControlAccessor().update(updated_file_process_message)
            else:
                logger.info("Passing processed file S3 path to patient ecosystem.")
                logger.info("Processed file for patient: " + str(updated_file_process_message))


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

    except Exception:
        raise

    else:
        return communicate_s3_patienteco_ruleengine(unicode_free_dictionary, new_file_path, key)


def communicate_s3_patienteco_ruleengine(file_process_dictionary, new_file_path, key):

    new_file_name = secure_filename(os.path.basename(new_file_path))
    new_file_s3_path = file_process_dictionary['ion_reporter_id'] + "/" + file_process_dictionary['molecular_id'] + \
                        "/" + file_process_dictionary['analysis_id'] + "/" + new_file_name
    try:
        S3Accessor().upload(new_file_path, new_file_s3_path)
    except Exception as e:
        logger.error(MESSAGE_SERVICE_FAILURE.substitute(service_name='S3', s3_path= new_file_s3_path,
                                                        path= 'None', message=e.message))
        raise Exception(MESSAGE_SERVICE_FAILURE.substitute(service_name='S3', s3_path= new_file_s3_path,
                                                        path= 'None', message=e.message))
    else:
        file_process_dictionary.update({key: new_file_s3_path})
        if key == 'tsv_name':
            if file_process_dictionary['molecular_id'].startswith('SC_'):
                # process rule engine for tsv file for sample_control only
                try:
                    file_process_dictionary = process_rule_by_tsv(file_process_dictionary, new_file_name)
                except Exception as e:
                    logger.error(MESSAGE_SERVICE_FAILURE.substitute(service_name='Rules Engine',
                                                                    s3_path= new_file_s3_path, path='None',
                                                                    message=e.message))
                    raise Exception(e.message)
            else:
                # post tsv name to patient ecosystem for patient only
                post_tsv_info(file_process_dictionary, new_file_name)

        # remove converted tsv or bai file from local machine
        if os.path.exists(new_file_path):
            os.remove(new_file_path)
        return file_process_dictionary


def process_vcf(dictionary):
    logger.info("Processing VCF.")
    try:
        downloaded_file_path = S3Accessor().download(dictionary['vcf_name'])
    except Exception as e:
        raise Exception(MESSAGE_SERVICE_FAILURE.substitute(service_name='S3', s3_path= dictionary['vcf_name'],
                                                           path= 'None', message=e.message))
    else:
        try:
            new_file_path = SequenceFileProcessor().vcf_to_tsv(downloaded_file_path)
        except Exception as e:
            logger.error(MESSAGE_CONVERSION_FAILURE.substitute(conversion_type='TSV from VCF',
                                                               s3_path= dictionary['vcf_name'],
                                                               path= downloaded_file_path, message=e.message))
            raise Exception(MESSAGE_CONVERSION_FAILURE.substitute(conversion_type='TSV from VCF',
                                                                  s3_path= dictionary['vcf_name'],
                                                                  path= downloaded_file_path, message=e.message))
        else:
            key = 'tsv_name'
            return new_file_path, key, downloaded_file_path


def process_bam(dictionary, nucleic_acid_type):
    logger.info("Processing " + nucleic_acid_type + " BAM ")
    try:
        downloaded_file_path = S3Accessor().download(dictionary[nucleic_acid_type + '_bam_name'])
    except Exception as e:
        raise Exception(MESSAGE_SERVICE_FAILURE.substitute(service_name='S3',
                                                           s3_path=dictionary[nucleic_acid_type + '_bam_name'],
                                                           path='None', message=e.message))
    else:
        try:
            new_file_path = SequenceFileProcessor().bam_to_bai(downloaded_file_path)
        except Exception as e:
            logger.error(MESSAGE_CONVERSION_FAILURE.substitute(conversion_type='BAI from BAM',
                                                               s3_path=dictionary[nucleic_acid_type + '_bam_name'],
                                                               path= downloaded_file_path, message=e.message))
            raise Exception(MESSAGE_CONVERSION_FAILURE.substitute(conversion_type='BAI from BAM',
                                                                  s3_path=dictionary[nucleic_acid_type + '_bam_name'],
                                                                  path= downloaded_file_path, message=e.message))
        else:
            key = nucleic_acid_type + '_bai_name'
            return new_file_path, key, downloaded_file_path


def post_tsv_info(dictionary, tsv_file_name):

    logger.info("Posting tsv file name to Patient Ecosystem for " + dictionary['molecular_id'])
    patient_url = (__builtin__.environment_config[__builtin__.environment]['patient_endpoint']
           + __builtin__.environment_config[__builtin__.environment]['patient_post_path'] + "/"
                   + dictionary['molecular_id'])
    headers = {'Content-type': 'application/json'}
    content = {'tsv_file_name': tsv_file_name,
               'ion_reporter_id': dictionary['ion_reporter_id'],
                'molecular_id': dictionary['molecular_id'],
                'analysis_id': dictionary['analysis_id']}

    try:
        r = requests.post(patient_url, data=json.dumps(content), headers=headers)
    except Exception as e:
        logger.error(MESSAGE_SERVICE_FAILURE.substitute(service_name='Patient Ecosystem',
                                                        s3_path=dictionary['tsv_name'],
                                                        path='None', message=e.message))
        raise Exception(MESSAGE_SERVICE_FAILURE.substitute(service_name='Patient Ecosystem',
                                                           s3_path=dictionary['tsv_name'],
                                                           path=patient_url, message=e.message))
    else:
        if str(r.status_code).startswith('20'):
            logger.info("Successfully posted TSV file name to Patient Ecosystem for " + dictionary['molecular_id'])
        else:
            logger.error(MESSAGE_SERVICE_FAILURE.substitute(service_name='Patient Ecosystem',
                                                            s3_path=dictionary['tsv_name'],
                                                           path='None', message=r.status_code))
            raise Exception(MESSAGE_SERVICE_FAILURE.substitute(service_name='Patient Ecosystem',
                                                               s3_path=dictionary['tsv_name'],
                                                               path=patient_url, message=r.status_code))


def process_rule_by_tsv(dictionary, tsv_file_name):

    logger.info("Reading rules engine for " + dictionary['molecular_id'])

    item = SampleControlAccessor().get_item({'molecular_id': dictionary['molecular_id']})
    if len(item) > 0:
        control_type = item['control_type']
    else:
        raise Exception("Cannot get control_type for "+ dictionary['molecular_id'])

    url = (__builtin__.environment_config[__builtin__.environment]['rule_endpoint']
           + __builtin__.environment_config[__builtin__.environment]['rule_path'])

    url = url + control_type + "/" + dictionary['ion_reporter_id'] + "/" + dictionary['molecular_id'] \
        + "/" + dictionary['analysis_id'] + "/" + tsv_file_name.split(".")[0] + "?format=tsv"

    try:
        headers = {'Content-type': 'application/json'}
        rule_response = requests.post(url, data=json.dumps([]), headers=headers)
    except Exception as e:
        logger.error(MESSAGE_SERVICE_FAILURE.substitute(service_name='Rules Engine', s3_path=dictionary['tsv_name'],
                                                        path=url, message=e.message))
        raise Exception(MESSAGE_SERVICE_FAILURE.substitute(service_name='Rules Engine', s3_path=dictionary['tsv_name'],
                                                        path=url, message=e.message))
    else:
        if rule_response.status_code ==200:
            var_dict = rule_response.json()
            for key, value in var_dict.iteritems():
                dictionary.update({key: value})
            dictionary.update({'date_variant_received': str(datetime.datetime.utcnow())})
        else:
            logger.error(MESSAGE_SERVICE_FAILURE.substitute(service_name='Rules Engine',
                                                            s3_path=dictionary['tsv_name'],
                                                            path=url, message=rule_response.status_code))
            raise Exception('Error Code: ' + str(rule_response.status_code))
    return dictionary


