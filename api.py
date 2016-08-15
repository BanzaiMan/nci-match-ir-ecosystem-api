#import json
import os.path

import boto3
from flask import Flask, jsonify, request
from flask.ext.cors import CORS
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.wsgi import WSGIContainer
from werkzeug.utils import secure_filename

from boto3.dynamodb.conditions import Key
import requests

#from bed_parser.ion_torrent_suite_bed import IonTorrentSuiteBed
#from s3_transfer import aws
#from s3_transfer.aws import S3Service

from dynamodb import aws
from dynamodb.aws import DynamoDBService

#from misc.progress_percentage import ProgressPercentage

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

#query the max value
'''
from boto.dynamodb2.table import Table as awsTable

tb = awsTable("MYTABLE")
rs = list(tb.query_2(PRIMARYKEY__eq="value", reverse=True, limit=1))
MAXVALUE = rs[0][RANGE_KEY]

'''


POSITIVE_CONTROL_TABLE = 'positive_sample_control'
SAMPLE_CONTROL_ID_PATTERN = 'SampleControl'
NON_TEMPLATE_CONTROL_TABLE = 'no_template_sample_control'
NTC_CONTROL_ID_PATTERN = 'NtcControl'

POSITIVE_SAMPLE = 'positive'
NON_TEMPLATE_SAMPLE = 'non_template'

SAVE_MOLECULAR_ID_URL = 'http://localhost:5001/api/ir/create_control_item?table_name=%s&partition_key_value=%s&molecular_id=%s&site_ip_address=129.43.127.133'

sites = ['MoCha', 'MDACC']

#POSITIVE_CONTROL_TABLE = 'sampleControl'
#NON_TEMPLATE_CONTROL_TABLE = 'ntcControl'


# message body template
message_body = """patient_id: {patient_id}
molecular_id: {molecular_id}
analysis_id: {analysis_id}
site: {site}
bucket: {bucket}
tsv_file_name: {tsv_file_name}
vcf_file_name: {vcf_file_name}
dna_bam_file_name: {dna_bam_file_name}
cdna_bam_file_name: {cdna_bam_file_name}
dna_bai_file_name: {dna_bai_file_name}
cdna_bai_file_name: {cdna_bai_file_name}
"""



@app.route('/api/ir_eco/version', methods=['GET'])
def version():
    return jsonify({'api_version': '0.1'})

@app.route('/api/ir_eco/test', methods=['GET'])
def test():
    return jsonify({'test': 'flask is running ok.'})


#curl -X GET 'http://localhost:5000/api/ir_eco/create_molecular_id?site=MoCha&sample_type=positive'
@app.route('/api/ir_eco/create_molecular_id', methods=['GET'])
def create_molecular_id():
    site = request.args.get('site')
    sample_type = request.args.get('sample_type')
    initialize_id = request.args.get('initial')

    if not site in sites:
        return jsonify({'error': 'site missing or not valid.'})

    print 'site', site
    print 'sample_type', sample_type

    #to-do: need to validate site

    if sample_type == POSITIVE_SAMPLE:
        sample_name_pattern = SAMPLE_CONTROL_ID_PATTERN
        table_name = POSITIVE_CONTROL_TABLE
    elif sample_type == NON_TEMPLATE_SAMPLE:
        sample_name_pattern = NTC_CONTROL_ID_PATTERN
        table_name = NON_TEMPLATE_CONTROL_TABLE
    else:
        return jsonify({'error': 'sample type missing or not valid.'})

    if initialize_id == 'true':
        new_molecular_id = sample_name_pattern+'_'+site+'_1'
    else:
        print 'table:', table_name
        dynamo_db = boto3.resource('dynamodb', region_name='us-west-2')
        #db_service = DynamoDBService()
        #ynamo_db = db_service.get_db_connection()
        control_table = dynamo_db.Table(table_name)
        response = control_table.query(
            KeyConditionExpression=Key('site').eq(site), ScanIndexForward=False, Limit=1
        )
        if response[u'Count'] != 1:
            return jsonify({'error': 'site not found in the db or unknown error happened.'})

        for item in response[u'Items']:
            latest_molecular_id = item['molecular_id']

        new_molecular_id = '_'.join(latest_molecular_id.split('_')[:-1])+'_'+str(int(latest_molecular_id.split('_')[-1])+1)
    r = requests.get(SAVE_MOLECULAR_ID_URL % (table_name, site, new_molecular_id))
    if 'SUCCESS' in r.text:
    #to-do: call processer's API to save the molecular id to database
        return jsonify({'new molecular id created:': new_molecular_id})
    else:
        return jsonify({'error:': 'failed to create new id.'})



#curl -X GET 'http://localhost:5000/api/ir_eco/validate_molecular_id?molecualr_id=SampleControl_MDACC_1'
@app.route('/api/ir_eco/validate_molecular_id', methods=['GET'])
def validate_molecular_id():
    #to-do: adding patient validation
    molecular_id = request.args.get('molecular_id')
    validation = validate_sample_control_id(molecular_id)
    return jsonify({'validation_result': bool(validation), 'date_created': str(validation)})


@app.route('/api/ir_eco/post_message', methods=['GET'])
def post_message():

    #get sqs resource
    sqs = boto3.resource('sqs', region_name='us-west-2')

        #get ir queue

    ir_queue = sqs.get_queue_by_name(QueueName='ir_queue_dev')

        #post the message
    molecular_id = request.args.get('molecular_id')
    analysis_id = request.args.get('analysis_id')
    patient_id = request.args.get('patient_id')
    site = request.args.get('site')
    bucket = request.args.get('bucket')
    tsv_file_name = request.args.get('tsv_file_name')
    vcf_file_name = request.args.get('vcf_file_name')
    dna_bam_file_name = request.args.get('dna_bam_file_name')
    cdna_bam_file_name = request.args.get('cdna_bam_file_name')
    dna_bai_file_name = request.args.get( 'dna_bai_file_name')
    cdna_bai_file_name = request.args.get('cdna_bai_file_name')

    data = {'molecular_id': molecular_id,
            'analysis_id': analysis_id,
            'patient_id': patient_id,
            'site': site,
            'bucket': bucket,
            'tsv_file_name': tsv_file_name,
            'vcf_file_name': vcf_file_name,
            'dna_bam_file_name': dna_bam_file_name,
            'cdna_bam_file_name': cdna_bam_file_name,
            'dna_bai_file_name': dna_bai_file_name,
            'cdna_bai_file_name': cdna_bai_file_name}

    real_message = message_body.format(**data)

    response = ir_queue.send_message(MessageBody=real_message)

    if response['ResponseMetadata']['HTTPStatusCode']==200:
        return jsonify(data)
    else:
        return jsonify({'Result': 'Message send failed'})


def validate_sample_control_id(molecular_id):
    tables = [POSITIVE_CONTROL_TABLE, NON_TEMPLATE_CONTROL_TABLE]
    #db_service = DynamoDBService()

    dynamo_db = boto3.resource('dynamodb', region_name='us-west-2')

    for table in tables:
        print molecular_id
        #dynamo_db = db_service.get_db_connection()
        control_table = dynamo_db.Table(table)
        site = molecular_id.split('_')[1]
        response = control_table.query(
            KeyConditionExpression=Key('site').eq(site)
        )
        id_date = {}
        for i in response[u'Items']:
            if not i['molecular_id'] in id_date:
                id_date[i['molecular_id']] = [i['date_molecular_id_created']]
            else:
                id_date[i['molecular_id']] = id_date[i['molecular_id']].append(i['date_molecular_id_created'])

        #print ids
        #print 'molecular id exist?'
        if molecular_id in id_date and len(id_date[molecular_id]) == 1:
            return id_date[molecular_id]
        #return molecular_id in ids

    return None



# def validate_ntc_control_id(molecular_id):
#     # molecular_id = request.args.get('molecular_id')
#     db_service = DynamoDBService()
#     dynamo_db = db_service.get_db_connection()
#     control_table = dynamo_db.Table(NTC_CONTROL_TBL)  # table_name hard-coded for now
#     response = control_table.query(
#         # KeyConditionExpression=Key('molecular_id').eq('_'.join(msn.split('_')[1:]))
#         KeyConditionExpression=Key('molecular_id').eq(molecular_id)
#     )
#     return int(response['Items']) > 0



if __name__ == '__main__':
    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(port=5001)
    IOLoop.instance().start()
