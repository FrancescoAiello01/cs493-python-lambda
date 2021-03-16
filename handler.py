from __future__ import print_function
# import json
# import boto3
# import logging


def logger(event, context):
    for record in event['Records']:
       payload=record["body"]
       print(str(payload))
    # # Setup logger
    # logger = logging.getLogger()
    # logger.setLevel(logging.INFO)
    # # Create SQS client
    # sqs = boto3.resource('sqs')
    # queue = sqs.get_queue_by_name(QueueName='music')
    
    # messages = []
    # for message in queue.receive_messages(MessageAttributeNames=['music']):
    #     # Get the custom author message attribute if it was set
    #     messages.append(message.body)
    #     # Let the queue know that the message is processed
    #     message.delete()
    # logger.info(f'Song played: {messages}')
    # return messages