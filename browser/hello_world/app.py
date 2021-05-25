import boto3
import re
import datetime
from functools import reduce

# import requests

def nameToDate(name):
    m = re.search(r"(\d*)_(\d*)_(\d*)_(\d*)_(\d*)_(\d*)",name)
    if(m == None):
        return None
    d = datetime.datetime(int(m.group(1)),int(m.group(2)),int(m.group(3)),int(m.group(4)),int(m.group(5)))
    return d

def prettyDate(d):
    return d.strftime("%a %b %-d, %-I:%M %p")


def list_videos(event, context):
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
    path = "https://disco-videos.s3.amazonaws.com/"

    # for object in bucket.objects.all():
    #     body += f'<a href="http://disco-videos.s3-website-us-west-2.amazonaws.com/{object.key}<br>'

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
