import boto3
import botocore
import json
import re
import os
import datetime
import logging
import pymysql
import sys
from pymysql.constants import CLIENT

from functools import reduce

from discodb import DiscoDB



logger = logging.getLogger()
logger.setLevel(logging.INFO)

##------------------------------------------------------------------------------------------------------------------------------
## globals
##------------------------------------------------------------------------------------------------------------------------------

botoConfig = botocore.config.Config(s3={'addressing_style':'path'})
s3 = boto3.resource('s3',config=botoConfig)

dbUsername = os.environ['DBUSERNAME']
dbPassword = os.environ['DBPASSWORD']
dbConnection = os.environ['DBCONNECTION']
dbName = os.environ['DBNAME']

try:
    #logger.info(f'connecting with c:{dbConnection}, u:{dbUsername}, p:{dbPassword}')
    db = DiscoDB(username=dbUsername,password=dbPassword,host=dbConnection,dbName=dbName)
    db.connect()
except pymysql.MySQLError as e:
    logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
    logger.error(e)
    sys.exit()
logger.info("SUCCESS: Connection to RDS MySQL instance succeeded")


jsonHeaders = {
                "Content-Type": "application/json",
                "Access-Control-Allow-Headers": 
                    "Content-Type,Authorization,X-Amz-Date,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": 
                    "DELETE,GET,HEAD,OPTIONS,PATCH,POST,PUT",
                "Access-Control-Allow-Origin": 
                    "*"
            }


##------------------------------------------------------------------------------------------------------------------------------
## utility functions
##------------------------------------------------------------------------------------------------------------------------------

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
    body = f'''<video controls>
                <source src="http://disco-videos.s3-website-us-west-2.amazonaws.com/{videoName}" type="video/mp4">
                Your browser does not support the video tag.
            </video>
            '''       
    return {
        "statusCode": 200,
        "body": body,
        "headers": {
            "Content-Type": "text/html"
        },
    }
def convertDates(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()

def toJson(o):
    return json.dumps(o, default = convertDates)

##------------------------------------------------------------------------------------------------------------------------------
## HomePage
##------------------------------------------------------------------------------------------------------------------------------

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


    bucketName = "disco-videos"

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

##------------------------------------------------------------------------------------------------------------------------------
## Hello World
##------------------------------------------------------------------------------------------------------------------------------
    

def hello_world(event, context):
    return {
        "statusCode": 200,
        "body": '["hello, world"]',
        "headers": jsonHeaders,
    }

##------------------------------------------------------------------------------------------------------------------------------
## List Videos
##------------------------------------------------------------------------------------------------------------------------------

def list_dances(event, context):
    rows = db.listDances()
    body = toJson({
        "result":0,
        "rows": rows
    })

    return {
        "statusCode": 200,
        "body": body,
        "headers": jsonHeaders,
    }

##------------------------------------------------------------------------------------------------------------------------------
## List Videos
##------------------------------------------------------------------------------------------------------------------------------

def get_dance(event, context):

    danceId = event['pathParameters']['id']

    result = 0
    row = db.getDanceById(int(danceId))
    if(row == None):
        row = {}
        result = -1

    body = toJson({
        "result":result,
        "dance": row
    })

    return {
        "statusCode": 200,
        "body": body,
        "headers": jsonHeaders,
    }

##------------------------------------------------------------------------------------------------------------------------------
## create new dance
##------------------------------------------------------------------------------------------------------------------------------

def create_dance(event, context):

    newDance = db.createDance()
    body = toJson({
        "result":0,
        "dance": newDance
    })
    return {
        "statusCode": 200,
        "body": body,
        "headers": jsonHeaders,
    }


##------------------------------------------------------------------------------------------------------------------------------
## update dance
##------------------------------------------------------------------------------------------------------------------------------

def update_dance(event, context):
    dbScript = '''
SELECT * FROM Dance ORDER BY time;
'''    
    logger.info("Connecting to DB")

    with conn.cursor() as cur:
        cur.execute(dbScript)

    logger.info("SUCCESS Connected to DB")
    return {
        "statusCode": 200,
        "body": "{}",
        "headers": jsonHeaders,
    }


##------------------------------------------------------------------------------------------------------------------------------
## delete dance
##------------------------------------------------------------------------------------------------------------------------------

def delete_dance(event, context):
    dbScript = '''
SELECT * FROM Dance ORDER BY time;
'''    
    logger.info("Connecting to DB")

    with conn.cursor() as cur:
        cur.execute(dbScript)

    logger.info("SUCCESS Connected to DB")
    return {
        "statusCode": 200,
        "body": "{}",
        "headers": jsonHeaders,
    }

##------------------------------------------------------------------------------------------------------------------------------
## DB Init
##------------------------------------------------------------------------------------------------------------------------------
def init_db(event, context):

    db.resetTables()

    return {
        "statusCode": 200,
        "body": "{}",
        "headers": jsonHeaders,
    }