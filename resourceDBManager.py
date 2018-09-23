import os
import boto3

USERS_TABLE = os.environ['USERS_TABLE']
STATES_TABLE = os.environ['STATES_TABLE']
IS_OFFLINE = os.environ.get('IS_OFFLINE')

if IS_OFFLINE:
    resourceDB = boto3.resource(
        'dynamodb',
        region_name='localhost',
        endpoint_url='http://localhost:8000'
    )
else:
    resourceDB = boto3.resource('dynamodb')