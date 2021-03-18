import json
from firebase_admin import credentials, auth
import firebase_admin

def generate_policy(allow):
    return {
        'principalId': 'token' ,
        'policyDocument': {
            'Version': '2012-10-17',
            'Statement': {
                'Action': 'execute-api:Invoke',
                'Effect': 'Allow' if allow else 'Deny',
                'Resource': 'arn:aws:lambda:us-east-1:513502687153:function:serverless-flask-dev-app'
            }
        }
    }

#Connect to firebase
cred = credentials.Certificate('fbAdminConfig.json')
firebase = firebase_admin.initialize_app(cred)

def handler(event, context):
    token = event['headers']['Authorization']
    print(event, token)
    if not token:
        generate_policy(False)
    try:
        decoded_token = auth.verify_id_token(token)
        uid = decoded_token['uid']
    except:
        return generate_policy(False)
    return generate_policy(True)
    