import boto3
import json
import re
import datetime
from functools import reduce

# import requests

def nameToDate(name):
    m = re.search(r"videos/(\d*)_(\d*)_(\d*)_(\d*)_(\d*)_(\d*)",name)
    if(m == None):
        return None
    d = datetime.datetime(int(m.group(1)),int(m.group(2)),int(m.group(3)),int(m.group(4)),int(m.group(5)))
    return d

def prettyDate(d):
    return d.strftime("%a %b %-d, %-I:%M %p")

def show_video(event, context):

    videoName = event['pathParameters']['id']
#    videoName = ""
    body = f'''<video controls>
                <source src="http://disco-videos.s3-website-us-west-2.amazonaws.com/{videoName}" type="video/mp4">
                Your browser does not support the video tag.
            </video>
            '''        

    # print(f'event resource is: {event["resource"]}')
    #  return {
    #     "statusCode": 200,
    #     "body": '',
    #     "headers": {
    #         "Content-Type": "application/json"
    #     },
    # }

    return {
        "statusCode": 200,
        "body": body,
        "headers": {
            "Content-Type": "text/html"
        },
    }

def homepage(event, context):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """

    # try:
    #     ip = requests.get("http://checkip.amazonaws.com/")
    # except requests.RequestException as e:
    #     # Send some context about this error to Lambda Logs
    #     print(e)

    #     raise e


    bucketName = "disco-videos"

    s3 = boto3.resource('s3')
    body = ""
    bucket = s3.Bucket(bucketName)
    path = "http://disco-videos.s3-website-us-west-2.amazonaws.com/"

    # for object in bucket.objects.all():
    #     body += f'<a href="http://disco-videos.s3-website-us-west-2.amazonaws.com/{object.key}<br>'

    files = bucket.objects.filter(Prefix='videos/')
    files = bucket.objects.all()
    files = map(lambda x: x.key,files)
    files = sorted(files,reverse=True)
    # only mp4s
    files = filter(lambda x: x.find("mp4") > 0,files)
    # extract dates
    files = map(lambda x: (x,nameToDate(x)),files)
    # remove poorly formatted files
    files = filter(lambda x: x[1] != None,files)
    files = map(lambda x: f'<a href="{path}{x[0]}">{prettyDate(x[1])}</a><br>',files)
    body = reduce(lambda a,b:a+b,files,"")


    return {
        "statusCode": 200,
        "body": body,
        "headers": {
            "Content-Type": "text/html"
        },
    }

def list_videos(event, context):

    bucketName = "disco-videos"

    s3 = boto3.resource('s3')
    body = ""
    bucket = s3.Bucket(bucketName)
    path = "http://disco-videos.s3-website-us-west-2.amazonaws.com/"

    # for object in bucket.objects.all():
    #     body += f'<a href="http://disco-videos.s3-website-us-west-2.amazonaws.com/{object.key}<br>'

    files = bucket.objects.filter(Prefix='videos/')
    files = bucket.objects.all()
#    files = map(lambda x: re.search(r"videos/(.*)\.mp4",x.key).group(1),files)
    files = map(lambda x: {"key":x.key},files)
#    files = sorted(files,reverse=True)
    body = json.dumps(list(files))


    return {
        "statusCode": 200,
        "body": body,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Headers": 
                "Content-Type,Authorization,X-Amz-Date,X-Api-Key,X-Amz-Security-Token",
            "Access-Control-Allow-Methods": 
                "DELETE,GET,HEAD,OPTIONS,PATCH,POST,PUT",
            "Access-Control-Allow-Origin": 
                "*"
        },
    }
