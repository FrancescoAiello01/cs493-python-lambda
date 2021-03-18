from __future__ import print_function


def logger(event, context):
    for record in event['Records']:
       payload=record["body"]
       print(str(payload))
       