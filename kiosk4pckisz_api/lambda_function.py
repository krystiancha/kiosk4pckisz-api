import json
from datetime import datetime
from logging import getLogger, INFO

from boto3 import resource

from kiosk4pckisz_api.encoders import DynamoDBEncoder


def lambda_handler(event=None, context=None):
    logger = getLogger()
    logger.setLevel(INFO)

    if event:
        try:
            identity = event['requestContext']['identity']
            logger.info('Identity: {} @ {}'.format(identity['userAgent'], identity['sourceIp']))
        except KeyError:
            logger.info('Identity: unknown')
    else:
        logger.info('Identity: unknown')

    dynamodb = resource('dynamodb')
    movies_table = dynamodb.Table('kiosk4pckisz-movies')
    shows_table = dynamodb.Table('kiosk4pckisz-shows')

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "movies": sorted(movies_table.scan()['Items'], key=lambda movie: movie['id']),
                "shows": sorted(shows_table.scan()['Items'], key=lambda show: datetime.strptime(show['start'], "%Y-%m-%d %H:%M:%S")),
            },
            cls=DynamoDBEncoder,
            ensure_ascii=False,
        ),
        'headers': {
            'Access-Control-Allow-Origin': '*'
        },
    }
