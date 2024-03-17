import time
import boto3

request_queue_url = 'https://sqs.us-east-1.amazonaws.com/654654147126/1227629236-req-queue'

sqs = boto3.client('sqs', region_name="us-east-1")
ec2 = boto3.client('ec2', region_name="us-east-1")

def groupInstances(appTierInstances):
    groupedInstances = {'stopping': [], 'running': [],  'stopped': [], 'pending': []}
    for x in appTierInstances['Reservations']:
        for i in x['Instances']:
            groupedInstances[i['State']['Name']].append(i['InstanceId'])

    return groupedInstances

def getMessageCount():
    attr = sqs.get_queue_attributes(QueueUrl=request_queue_url,AttributeNames=['ApproximateNumberOfMessages'])
    return int(attr['Attributes']['ApproximateNumberOfMessages'])

def getActiveInstances(groupedInstances):
    return len(groupedInstances['running']) + len(groupedInstances['pending'])

def scale():
    while True:
        try:
            appTierInstances = ec2.describe_instances(Filters=[{'Name': 'tag:Name', 'Values': ["app-tier-instance*"]},{'Name': 'instance-state-name', 'Values': ['running', 'stopped', 'pending', 'stopping']}])
            groupedInstances = groupInstances(appTierInstances)
            activeInstances = getActiveInstances(groupedInstances)
            if activeInstances:
                print(activeInstances)
            messages = min(20, getMessageCount())
            if messages - activeInstances > 0:
                if groupedInstances['stopped']:
                    ec2.start_instances(InstanceIds=groupedInstances['stopped'][:(messages - activeInstances)])
                    time.sleep(5)
            elif messages - activeInstances < 0:
                if groupedInstances['running']:
                    ec2.stop_instances(InstanceIds=groupedInstances['running'][:abs(messages - activeInstances)])
                    time.sleep(5)
        except Exception as e:
            print("Error: ", e)


if __name__ == "__main__":
    scale()