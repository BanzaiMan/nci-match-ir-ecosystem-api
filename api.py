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

POSITIVE_CONTROL_TABLE = 'sampleControl'
NON_TEMPLATE_CONTROL_TABLE = 'ntcControl'


# message body template
message_body = """patient_id: {patient_id},
molecular_id: {molecular_id},
analysis_id: {analysis_id},
s3_path: {s3_path}
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


# curl -X GET 'http://localhost:5000/api/ir_eco/validate_molecular_id?molecualr_id=SampleControl_MDACC_1'
@app.route('/api/ir_eco/validate_molecular_id', methods=['GET'])
def validate_sample_control_msn():
    molecular_id = request.args.get('molecular_id')
    validation = validate_sample_control(molecular_id)
    return jsonify({'validation_result': str(validation)})


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
    s3_path = request.args.get('s3_path')
    tsv_file_name = request.args.get('tsv_file_name')
    vcf_file_name = request.args.get('vcf_file_name')
    dna_bam_file_name = request.args.get('dna_bam_file_name')
    cdna_bam_file_name = request.args.get('cdna_bam_file_name')
    dna_bai_file_name = request.args.get( 'dna_bai_file_name')
    cdna_bai_file_name = request.args.get('cdna_bai_file_name')

    data = {'molecular_id': molecular_id,
            'analysis_id': analysis_id,
            'patient_id': patient_id,
            's3_path': s3_path,
            'tsv_file_name': tsv_file_name,
            'vcf_file_name': vcf_file_name,
            'dna_bam_file_name': dna_bam_file_name,
            'cdna_bam_file_name': cdna_bam_file_name,
            'dna_bai_file_name': dna_bai_file_name,
            'cdna_bai_file_name': cdna_bai_file_name}

    real_message = message_body.format(**data)

    response = ir_queue.send_message(MessageBody=real_message)
    return jsonify(response)


def validate_sample_control(molecular_id):
    tables = [POSITIVE_CONTROL_TABLE, NON_TEMPLATE_CONTROL_TABLE]
    db_service = DynamoDBService()

    for table in tables:
        dynamo_db = db_service.get_db_connection()
        control_table = dynamo_db.Table(table)
        response = control_table.query(
            #KeyConditionExpression=Key('molecualr_id').eq('_'.join(msn.split('_')[1:]))
            KeyConditionExpression=Key('molecualr_id').eq(molecular_id)
        )
        if int(response['Items']) > 0:
            return True

    return False



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
    http_server.listen(port=5000)
    IOLoop.instance().start()
