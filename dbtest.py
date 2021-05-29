import logging
import sys
import pymysql
import os


logger = logging.getLogger()
logger.setLevel(logging.INFO)


dbUsername = #os.environ['DBUSERNAME']
dbPassword = #os.environ['DBPASSWORD']
dbConnection = "disco-serverless-db.cluster-c4xguvxrtngc.us-west-2.rds.amazonaws.com" #os.environ['DBCONNECTION']

try:
    logger.info(f'connecting with c:{dbConnection}, u:{dbUsername}, p:{dbPassword}')
    conn = pymysql.connect(host=dbConnection, port=3306, user=dbUsername, passwd=dbPassword, db:dbHost, connect_timeout=2)
except pymysql.MySQLError as e:
    logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
    logger.error(e)
    sys.exit()
logger.info("SUCCESS: Connection to RDS MySQL instance succeeded")
