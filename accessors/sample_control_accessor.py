from dynamodb_accessor import DynamoDBAccessor


class SampleControlAccessor(DynamoDBAccessor):

    def __init__(self):
        DynamoDBAccessor.__init__(self, 'sample_controls')
