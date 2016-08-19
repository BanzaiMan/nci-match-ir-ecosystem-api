import random
import string

from dynamodb.dynamodb_utility import sanitize, get_utc_millisecond_timestamp, DecimalEncoder
from dynamodb_accessor import DynamoDBAccessor
from boto3.dynamodb.conditions import Key
import boto3


class SampleControlAccessor(DynamoDBAccessor):

    def __init__(self):
        DynamoDBAccessor.__init__(self, 'sample_controls')

    def query_sample_controls(self, query_parameters):

        #TODO: CREATE QUERY DYNAMICALLY
        # the query parameters can be passed in the format {'site':'mocha', 'type':'positive'}
        # This is just a dictionary with 0 to 3 values. You Don't need to know what was passed in just create
        # a query
        if 'id' in query_parameters:
            molecular_id = query_parameters['id']
            if 'site' in query_parameters:
                site = query_parameters['site']
                results = get_item_by_molecular_id_and_site(site, id)
            else:
                results = get_item_by_molecular_id(id)
        elif 'site' in query_parameters:
            site = query_parameters['site']
            if 'type' in query_parameters:
                sample_type = query_parameters['type']
                results = get_item_by_site_and_type(site, sample_type)
            else:
                results = get_item_by_site_and_type[site]
        elif 'type' in query_parameters:
            sample_type = query_parameters['type']
            results = get_item_by_type(sample_type)
        else:
            results = get_all_items()



        results = self.table.get_item(Key={'id': 'SC_45RT6', 'site': 'mocha'})
        print results

    def get_item_by_molecualr_id(self, molecular_id):
        pass

    def get_sample_controls(self):
        return "hi"
    # def get_new_molecular_id(self, table_name, site):
    #     dynamo_db = self.get_db_connection()
    #     control_table = dynamo_db.Table(table_name)
    #     response = control_table.query(
    #         KeyConditionExpression=Key('site').eq(site), ScanIndexForward=False, Limit=1
    #     )
    #     if response['Count'] != 1:
    #         print 'error: nothing found or more than one items returned.'
    #         return
    #         #return jsonify({'error': 'site not found in the db or unknown error happened.'})
    #
    #     for item in response['Items']:
    #         latest_molecular_id = item['molecular_id']
    #
    #     new_molecular_id = '_'.join(latest_molecular_id.split('_')[:-1])+'_'+str(int(latest_molecular_id.split('_')[-1])+1)
    #     return new_molecular_id


    # @staticmethod
    # def id_generator(size=5, chars=string.ascii_uppercase + string.digits): #generate a random id
    #     return ''.join(random.choice(chars) for _ in range(size))
    #
    # def get_new_molecular_id(self, site, sample_type):
    #     #create a random id
    #     new_molecular_id = 'SampleControl_'+SampleControlAccessor.id_generator()
    #     new_molecular_id = 'SampleControl_SAWCB'
    #     while self.molecular_id_exist(new_molecular_id, site):
    #         print 'doing molecular_id check:'
    #         new_molecular_id = 'SampleControl_'+SampleControlAccessor.id_generator()
    #
    #     date_created = get_utc_millisecond_timestamp()
    #     site_ip_address = SITE_IP_ADDRESSES[site]
    #     self.insert_control_item(site, date_created, new_molecular_id, sample_type, site_ip_address)
    #     print 'new_molecular_id', new_molecular_id
    #     return new_molecular_id
    #     #validate it in db
    #     #commit it in db along with site and type
    #     #pass
    #
    # def insert_control_item(self, partition_key_value, sort_key_value,
    #                         molecular_id, sample_type, site_ip_address):
    #     #dynamo_db = self.get_local_connection()
    #     dynamo_db = self.get_db_connection()
    #     table = dynamo_db.Table(TABLE_NAME)
    #     table.put_item(
    #         Item={
    #             'site': partition_key_value,
    #             'date_molecular_id_created': sort_key_value,
    #             'molecular_id': molecular_id,
    #             'type': sample_type,
    #             'site_ip_address': site_ip_address
    #         }
    #     )

    # # validate molecular_id existence in DB and only one creation_date associated.
    # def molecular_id_exist(self, molecular_id, site):
    #     # dynamo_db = self.get_local_connection()
    #     dynamo_db = self.get_db_connection()
    #     control_table = dynamo_db.Table(TABLE_NAME)
    #     # site = molecular_id.split('_')[1]
    #     response = control_table.query(
    #         KeyConditionExpression=Key('site').eq(site)
    #     )
    #     ids = []
    #     for item in response['Items']:
    #         ids.append(item['molecular_id'])
    #     return molecular_id in ids

    # # validate molecular_id existence in DB and only one creation_date associated.
    # def validate_molecular_id(self, molecular_id, site):
    #     #dynamo_db = self.get_local_connection()
    #     dynamo_db =self.get_db_connection()
    #     control_table = dynamo_db.Table(TABLE_NAME)
    #     #site = molecular_id.split('_')[1]
    #     response = control_table.query(
    #         KeyConditionExpression=Key('site').eq(site)
    #     )
    #     id_date = {}
    #     for item in response['Items']:
    #         if not item['molecular_id'] in id_date:
    #             print id_date
    #             print item['molecular_id']
    #             print item['date_molecular_id_created']
    #             id_date[item['molecular_id']] = [item['date_molecular_id_created']]
    #         else:
    #             print id_date
    #             print item['molecular_id']
    #             print item['date_molecular_id_created']
    #             id_date[item['molecular_id']].append(item['date_molecular_id_created'])
    #
    #     # print ids
    #     # print 'molecular id exist?'
    #     print id_date
    #     if molecular_id in id_date:
    #         if len(id_date[molecular_id]) == 1:
    #         #print molecular_id
    #         #print id_date[molecular_id]
    #             return id_date[molecular_id]
    #
    #     return None
    #         # return molecular_id in ids

if __name__ == '__main__':
    tst_accessor = SampleControlAccessor()
    #print tst_accessor.get_new_molecular_id('MoCha')
    #print tst_accessor.get_new_molecular_id('MDACC')
    print tst_accessor.get_new_molecular_id2('MoCha', 'positive')


