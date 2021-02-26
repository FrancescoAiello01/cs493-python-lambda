from flask import Flask
from flask_cors import CORS, cross_origin
import boto3
import json

app = Flask(__name__)
CORS(app, support_credentials=True)


def add_to_music_dictionary(object_key, dictionary, signed_url):
    object_key = object_key.split("/")
    if object_key[0] not in dictionary:
        dictionary[object_key[0]] = {object_key[1]: {object_key[2]: signed_url}}
    elif object_key[1] not in dictionary[object_key[0]]:
        dictionary[object_key[0]][object_key[1]]: {object_key[2]: signed_url}
    else:
        dictionary[object_key[0]][object_key[1]][object_key[2]] = signed_url

    return dictionary


def create_presigned_url(bucket_name, object_key, expiration, s3_client):
    return s3_client.generate_presigned_url(
        "get_object",
        Params={"Bucket": bucket_name, "Key": object_key},
        ExpiresIn=expiration,
    )


@app.route("/")
@cross_origin(supports_credentials=True)
def get_music():
    s3_client = boto3.client("s3")
    s3 = boto3.resource("s3")

    bucket = s3.Bucket("demo-s3-bucket-cs493-2")
    bucket_content = s3_client.list_objects(Bucket="demo-s3-bucket-cs493-2")

    music = {}
    for object in bucket_content["Contents"]:
        object_key = object["Key"]
        signed_song_url = create_presigned_url(bucket.name, object_key, 500, s3_client)
        music = add_to_music_dictionary(object_key, music, signed_song_url)

    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
        },
        "body": json.dumps(music),
    }
