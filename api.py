#import json
import os.path

#import boto3
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

SAMPLE_CONTROL_TBL = 'sampleControl'
SAMPLE_CONTROL_ID_PATTERN = 'SampleControl'
NTC_CONTROL_TBL = 'ntcControl'
NTC_CONTROL_ID_PATTERN = 'NtcControl'


@app.route('/api/ir_eco/version', methods=['GET'])
def version():
    return jsonify({'api_version': '0.1'})

#curl -X GET 'http://localhost:5000/api/ir_eco/validate_molecular_id?molecualr_id=SampleControl_MDACC_1'
@app.route('/api/ir_eco/validate_molecular_id', methods=['GET'])
def validate_sample_control_msn():
    molecular_id = request.args.get('molecular_id')
    if molecular_id.startswith(SAMPLE_CONTROL_ID_PATTERN):
        validation = str(validate_sample_control_id(molecular_id))

    elif molecular_id.startswith(NTC_CONTROL_ID_PATTERN):
        validation = str(validate_ntc_control_id(molecular_id))

    else:
        #to_do: call patient validation api
        validation = False
    return jsonify({'validation_result: '+validation})


def validate_sample_control_id(molecular_id):
    #molecular_id = request.args.get('molecular_id')
    db_service = DynamoDBService()
    dynamo_db = db_service.get_db_connection()
    control_table = dynamo_db.Table(SAMPLE_CONTROL_TBL)#table_name hard-coded for now
    response = control_table.query(
        #KeyConditionExpression=Key('molecualr_id').eq('_'.join(msn.split('_')[1:]))
        KeyConditionExpression=Key('molecualr_id').eq(molecular_id)
    )
    return int(response['Items']) > 0

def validate_ntc_control_id(molecular_id):
    # molecular_id = request.args.get('molecular_id')
    db_service = DynamoDBService()
    dynamo_db = db_service.get_db_connection()
    control_table = dynamo_db.Table(NTC_CONTROL_TBL)  # table_name hard-coded for now
    response = control_table.query(
        # KeyConditionExpression=Key('molecualr_id').eq('_'.join(msn.split('_')[1:]))
        KeyConditionExpression=Key('molecular_id').eq(molecular_id)
    )
    return int(response['Items']) > 0











if __name__ == '__main__':
    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(port=5000)
    IOLoop.instance().start()
