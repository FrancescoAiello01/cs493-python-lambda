from flask import Flask
import boto3
import json

app = Flask(__name__)


@app.route("/")
def hello():
    s3 = boto3.resource("s3")
    s3_client = boto3.client("s3")

    # Your Bucket Name
    bucket = s3.Bucket("demo-s3-bucket-cs493-2")

    # Gets the list of objects in the Bucket
    s3_Bucket_iterator = bucket.objects.all()

    # Generates the Signed URL for each object in the Bucket
    urls = [
        s3_client.generate_presigned_url(
            ClientMethod="get_object", Params={"Bucket": bucket.name, "Key": i.key}
        )
        for i in s3_Bucket_iterator
    ]
    return json.dumps(urls, indent=4)
