import __builtin__
import ast
import json
import logging
import os
import urllib
import inspect
import datetime
from logging.config import fileConfig

import requests
from celery import Celery
from celery.exceptions import MaxRetriesExceededError
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
        'polling_interval': __builtin__.environment_config[__builtin__.environment]['polling_interval']
    }
    app = Celery('tasks', broker=BROKER__URL, broker_transport_options=BROKER_TRANSPORT_OPTIONS)
    app.conf.CELERY_ACCEPT_CONTENT = ['json']
    app.conf.CELERY_TASK_SERIALIZER = 'json'
    app.conf.CELERY_ACKS_LATE = True
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

slack_channel_id = (__builtin__.environment_config[__builtin__.environment]['slack_channel_id'])
requeue_countdown = (__builtin__.environment_config[__builtin__.environment]['requeue_countdown'])




# I don't think we will use this for sample control as our sample control creation of records are not done through
# the queueing system but directly on the database. However, I'll leave this for now.
@app.task
def put(put_message):
    logger.info("Creating item: " + str(put_message))
    try:
        SampleControlAccessor().put_item(put_message)
    except Exception as e:
        stack = inspect.stack()
        details = put.request
        logger.error("Put item failed, details: " +str(details))
        PedMatchBot.return_stack(queue_name, put_message, e.message, stack)
        # try:
        #     put.retry(args=[put_message], countdown=requeue_countdown)
        # except MaxRetriesExceededError:
        #     error = ("Maximum retries reached moving task to " + dlx_queue)
        #     logger.error(error)
        #     PedMatchBot.return_stack(queue_name, put_message, error, stack)
        #     put.apply_async(args=[put_message], queue=dlx_queue)


# Use for just updating the data in a record in the table
@app.task
def update(update_message):
    logger.info("Updating item: " + str(update_message))
    try:
        SampleControlAccessor().update(update_message)
    except Exception as e:
        stack = inspect.stack()
        details = update.request
        logger.error("Updating item failed, details: " +str(details))
        PedMatchBot.return_stack(queue_name, update_message, e.message, stack)
        # try:
        #     update.retry(args=[update_message], countdown=requeue_countdown)
        # except MaxRetriesExceededError:
        #     error = ("Maximum retries reached moving task to " + dlx_queue)
        #     logger.error(error)
        #     PedMatchBot.return_stack(queue_name, update_message, error, stack)
        #     update.apply_async(args=[update_message], queue=dlx_queue)


@app.task
def update_ir(update_message):
    logger.info("Updating item: " + str(update_message))
    try:
        IonReporterAccessor().update(update_message)
    except Exception as e:
        stack = inspect.stack()
        details = update_ir.request
        logger.error("Updating item failed, details: " +str(details))
        PedMatchBot.return_stack(queue_name, update_message, e.message, stack)
        # try:
        #     update_ir.retry(args=[update_message], countdown=requeue_countdown)
        # except MaxRetriesExceededError:
        #     error = ("Maximum retries reached moving task to " + dlx_queue)
        #     logger.error(error)
        #     PedMatchBot.return_stack(queue_name, update_message, error, stack)
        #     update_ir.apply_async(args=[update_message], queue=dlx_queue)


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

    try:
        # process vcf, dna_bam, or cdna_bam file
        updated_file_process_message = process_file_message(new_file_process_message)

    except Exception as e:
        stack = inspect.stack()
        details = process_ir_file.request
        logger.error("Process file message failed, details: " +str(details))
        PedMatchBot.return_stack(queue_name, new_file_process_message, e.message, stack)
        # try:
        #     process_ir_file.retry(args=[new_file_process_message], countdown=requeue_countdown)
        # except MaxRetriesExceededError:
        #     error = ("Maximum retries reached for " + str(new_file_process_message) + "moving task to " + dlx_queue)
        #     logger.error(error)
        #     PedMatchBot.return_stack(queue_name, new_file_process_message, error, stack)
        #     process_ir_file.apply_async(args=[new_file_process_message],queue=dlx_queue)
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
        logger.error("Failed to upload to S3 after processing file for " + str(new_file_s3_path) + ", because: "
                        + str(e.message))
        raise Exception("Failed to upload to S3 after processing file for " + str(new_file_s3_path) + ", because: "
                        + str(e.message))
    else:
        file_process_dictionary.update({key: new_file_s3_path})
        if key == 'tsv_name':
            if file_process_dictionary['molecular_id'].startswith('SC_'):
                # process rule engine for tsv file for sample_control only
                try:
                    file_process_dictionary = process_rule_by_tsv(file_process_dictionary, new_file_name)
                except Exception as e:
                    logger.error("Failed to read Rules Engine for " + new_file_name + ", because: " + str(e.message))
                    raise Exception("Failed to read Rules Engine for " + new_file_name + ", because: " + str(e.message))
            else:
                # post tsv name to patient ecosystem for patient only
                post_tsv_info(file_process_dictionary, new_file_name)
        return file_process_dictionary


def process_vcf(dictionary):
    logger.info("Processing VCF.")
    try:
        downloaded_file_path = S3Accessor().download(dictionary['vcf_name'])
    except Exception as e:
        raise Exception("Failed to download vcf file from S3, because: " + str(e.message))
    else:
        try:
            new_file_path = SequenceFileProcessor().vcf_to_tsv(downloaded_file_path)
        except Exception as e:
            logger.error("TSV creation failed because: " + str(e.message))
            raise Exception("TSV creation failed because: " + str(e.message))
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
            logger.error("BAI creation failed because: " + str(e.message))
            raise Exception("BAI creation failed because: " + str(e.message))
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
        logger.error("Failed to post TSV file name to Patient Ecosystem for " + str(dictionary['molecular_id'])
                        + ", because: " + str(e.message))
        raise Exception("Failed to post TSV file name to Patient Ecosystem for " + str(dictionary['molecular_id'])
                        + ", because: " + str(e.message))
    else:
        if r.status_code == 200:
            logger.info("Successfully posted TSV file name to Patient Ecosystem for " + dictionary['molecular_id'])
        else:
            stack = inspect.stack()
            error_message = "Posting of TSV to patient ecosystem failed for " + dictionary['molecular_id']
            logger.error("Posting of TSV to patient ecosystem failed for: " + dictionary['molecular_id'] +
                         " because error code: " + str(r.status_code))
            PedMatchBot.return_stack(queue_name, dictionary, error_message, stack)
            raise Exception(error_message)


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
        logger.error("Failed to get rules engine data for " + tsv_file_name + ", because: "
                        + str(e.message) + "URL = " + url)
        raise Exception("Failed to get rules engine data for " + tsv_file_name + ", because: "
                        + str(e.message) + "URL = " + url)
    else:
        if rule_response.status_code ==200:
            var_dict = rule_response.json()
            for key, value in var_dict.iteritems():
                dictionary.update({key: value})
            dictionary.update({'date_variant_received': str(datetime.datetime.utcnow())})
        else:
            error_msg = ("Failed to get rules engine data for: " + dictionary['molecular_id'] +
                         " because error status code: " + str(rule_response.status_code))
            logger.error(error_msg)
            stack = inspect.stack()
            PedMatchBot.return_stack(queue_name, dictionary, error_msg, stack)
            raise Exception(error_msg)
    return dictionary


@app.task
def delete(molecular_id):
    logger.info("Deleting sample control record with molecular id:" + str(molecular_id))
    try:
        SampleControlAccessor().delete_item(molecular_id)
    except Exception as e:
        stack = inspect.stack()
        details = delete.request
        logger.error("Deleting sample control record failed, details:" +str(details))
        PedMatchBot.return_stack(queue_name, molecular_id, e.message, stack)
        # try:
        #     delete.retry(args=[molecular_id], countdown=requeue_countdown)
        # except MaxRetriesExceededError:
        #     error = ("Maximum retries reached moving task to " + dlx_queue)
        #     logger.error(error)
        #     PedMatchBot.return_stack(queue_name, molecular_id, error, stack)
        #     delete.apply_async(args=[molecular_id], queue=dlx_queue)


@app.task
def delete_ir(ion_reporter_id):
    logger.info("Deleting ion reporter record with ion reporter id:" + str(ion_reporter_id))
    try:
        IonReporterAccessor().delete_item(ion_reporter_id)
    except Exception as e:
        stack = inspect.stack()
        details = delete_ir.request
        logger.error("Deleting ion reporter record failed, details:" +str(details))
        PedMatchBot.return_stack(queue_name, ion_reporter_id, e.message, stack)
        # try:
        #     delete_ir.retry(args=[ion_reporter_id], countdown=requeue_countdown)
        # except MaxRetriesExceededError:
        #     error = ("Maximum retries reached moving task to " + dlx_queue)
        #     logger.error(error)
        #     PedMatchBot.return_stack(queue_name, ion_reporter_id, error, stack)
        #     delete_ir.apply_async(args=[ion_reporter_id], queue=dlx_queue)

@app.task
def batch_delete(query_parameters):
    logger.info("Deleting sample control records matching query:" + str(query_parameters))
    try:
        SampleControlAccessor().batch_delete(query_parameters)
    except Exception as e:
        stack = inspect.stack()
        details = batch_delete.request
        logger.error("Deleting sample control record failed, details:" +str(details))
        PedMatchBot.return_stack(queue_name, query_parameters, e.message, stack)
        # try:
        #     batch_delete.retry(args=[query_parameters], countdown=requeue_countdown)
        # except MaxRetriesExceededError:
        #     error = ("Maximum retries reached moving task to " + dlx_queue)
        #     logger.error(error)
        #     PedMatchBot.return_stack(queue_name, query_parameters, error, stack)
        #     batch_delete.apply_async(args=[query_parameters], queue=dlx_queue)


@app.task
def batch_delete_ir(query_parameters):
    logger.info("Deleting ion reporter records matching query:" + str(query_parameters))
    try:
        IonReporterAccessor().batch_delete(query_parameters)
    except Exception as e:
        stack = inspect.stack()
        details = batch_delete_ir.request
        logger.error("Deleting ion reporter record failed, details:" +str(details))
        PedMatchBot.return_stack(queue_name, query_parameters, e.message, stack)
        # try:
        #     batch_delete_ir.retry(args=[query_parameters], countdown=requeue_countdown)
        # except MaxRetriesExceededError:
        #     error = ("Maximum retries reached moving task to " + dlx_queue)
        #     logger.error(error)
        #     PedMatchBot.return_stack(queue_name, query_parameters, error, stack)
        #     batch_delete_ir.apply_async(args=[query_parameters], queue=dlx_queue)