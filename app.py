from flask import Flask, Response, request
import pandas as pd
import boto3
import uuid

s3 = boto3.client('s3', 'us-east-1')
sqs = boto3.client('sqs', 'us-east-1')
request_queue_url = 'https://sqs.us-east-1.amazonaws.com/975049916042/1227629236-req-queue'
response_queue_url = 'https://sqs.us-east-1.amazonaws.com/975049916042/1227629236-resp-queue'
input_bucket = '1227629236-in-bucket'
app = Flask(__name__)

@app.route("/", methods=['POST'])
def send_request():
    file = request.files['inputFile']
    print("FILE: ",file.filename)
    s3.upload_fileobj(Fileobj=file, Bucket=input_bucket, Key=file.filename)
    request_id = str(uuid.uuid4())
    sqs.send_message(QueueUrl=request_queue_url,MessageBody=(file.filename), MessageAttributes={'RequestId': {'StringValue': request_id, 'DataType': 'String'}})

    while (True):
        try:
            response = sqs.receive_message(QueueUrl=response_queue_url,VisibilityTimeout=1,MaxNumberOfMessages=1,WaitTimeSeconds=10,MessageAttributeNames=['All'])
            messages = response.get('Messages', [])
            if messages:
                for message in messages:
                    if message.get('MessageAttributes', {}).get('RequestId', {}).get('StringValue') == request_id:
                        result = message['Body']
                        response = sqs.delete_message(QueueUrl=response_queue_url,ReceiptHandle=message['ReceiptHandle'])
                        return Response(result, status=200)
        except Exception as e:
            print("Error: ", e)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port="8000")
    
