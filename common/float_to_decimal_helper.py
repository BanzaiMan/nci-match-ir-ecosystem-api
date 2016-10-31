from decimal import Decimal
from collections import Mapping, Set, Sequence

#Python boto3 does not take float type, so convert float data to decimal before send to DynamoDB
def sanitize(data):
    # Sanitizes an object so it can be updated to dynamodb (recursive)
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
