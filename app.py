from flask import Flask, request
# from flask_cors import CORS, cross_origin
import boto3
import json

app = Flask(__name__)
# CORS(app, support_credentials=True)


def add_to_music_dictionary(object_key, dictionary, signed_url):
    object_key = object_key.split("/")
    if object_key[0] not in dictionary:
        dictionary[object_key[0]] = {object_key[1]: {object_key[2]: signed_url}}
    elif object_key[1] not in dictionary[object_key[0]] and object_key[1] != '.DS_Store':
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


@app.route("/") # cross_origin(supports_credentials=True)
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

    return music
    # return {
    #     "statusCode": 200,
    #     "headers": {
    #         "Access-Control-Allow-Headers": "Content-Type",
    #         "Access-Control-Allow-Origin": "*",
    #         "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
    #     },
    #     "body": json.dumps(music),
    # }


@app.route("/genres", methods=["GET"])
def get_genres():
    dynamodb_client = boto3.client('dynamodb', region_name="us-west-2")
    TABLE_NAME = "music"

    response = dynamodb_client.query(
        TableName=TABLE_NAME,
        KeyConditionExpression='#pk = :pk',
        ExpressionAttributeNames={
            '#pk': 'pk'
        },
        ExpressionAttributeValues={
            ':pk': { 'S': 'genre' },
        }
        )
    genres = []
    for item in response['Items']:
        genres.append(item['name']['S'])
    return str(genres)


@app.route("/artists/for/genre", methods=["GET"])
def get_artists_for_genre():
    dynamodb_client = boto3.client('dynamodb', region_name="us-west-2")
    TABLE_NAME = "music"
    genre = request.args.get("genre")

    response = dynamodb_client.query(
        TableName=TABLE_NAME,
        KeyConditionExpression='#pk = :pk and begins_with(#sk, :sk)',
        ExpressionAttributeNames={
            '#pk': 'pk',
            '#sk': 'sk'
        },
        ExpressionAttributeValues={
            ':pk': { 'S': f'genre#{genre}' },
            ':sk': { 'S': 'artist#' }
        }
        )
    artists = []
    for item in response['Items']:
        artists.append(item['name']['S'])
    return str(artists)


@app.route("/albums/for/artist", methods=["GET"])
def get_albums_for_artist():
    dynamodb_client = boto3.client('dynamodb', region_name="us-west-2")
    TABLE_NAME = "music"
    artist = request.args.get("artist")

    response = dynamodb_client.query(
        TableName=TABLE_NAME,
        KeyConditionExpression='#pk = :pk and begins_with(#sk, :sk)',
        ExpressionAttributeNames={
            '#pk': 'pk',
            '#sk': 'sk'
        },
        ExpressionAttributeValues={
            ':pk': { 'S': f'artist#{artist}' },
            ':sk': { 'S': 'album#' }
        }
        )
    albums = []
    for item in response['Items']:
        albums.append(item['name']['S'])
    return str(albums)


@app.route("/songs/for/album", methods=["GET"])
def get_songs_for_album():
    dynamodb_client = boto3.client('dynamodb', region_name="us-west-2")
    TABLE_NAME = "music"
    album = request.args.get("album")

    response = dynamodb_client.query(
        TableName=TABLE_NAME,
        KeyConditionExpression='#pk = :pk and begins_with(#sk, :sk)',
        ExpressionAttributeNames={
            '#pk': 'pk',
            '#sk': 'sk'
        },
        ExpressionAttributeValues={
            ':pk': { 'S': f'album#{album}' },
            ':sk': { 'S': 'song#' }
        }
        )
    song = []
    for item in response['Items']:
        song.append(item['name']['S'])
    return str(song)


@app.route("/song", methods=["GET"])
def get_song_url_from_name():
    dynamodb_client = boto3.client('dynamodb', region_name="us-west-2")
    s3_client = boto3.client("s3")
    TABLE_NAME = "music"
    song = request.args.get("song")

    response = dynamodb_client.query(
        TableName=TABLE_NAME,
        KeyConditionExpression='#pk = :pk',
        ExpressionAttributeNames={
            '#pk': 'pk',
        },
        ExpressionAttributeValues={
            ':pk': { 'S': f'song#{song}' },
        }
        )
    song = []
    for item in response['Items']:
        song.append(item['s3_key']['S'])
    url = create_presigned_url("demo-s3-bucket-cs493-2", song[0], 500, s3_client)
    return url


@app.route("/play", methods=["POST"])
def play():
    request_data = request.json
    # Create SQS client
    sqs = boto3.client('sqs')
    queue_url = 'https://sqs.us-east-1.amazonaws.com/513502687153/music'
    # Send message to SQS queue
    response = sqs.send_message(
        QueueUrl=queue_url,
        DelaySeconds=10,
        MessageBody=(
            json.dumps(request_data)
        )
    )
    return json.dumps(response)