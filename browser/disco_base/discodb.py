import pymysql
from pymysql.constants import CLIENT
import logging

logger = logging.getLogger()



class DiscoDB:
    def __init__(self,username,password,host,dbName):
        self.username = username
        self.password = password
        self.host = host
        self.dbName = dbName

    def connect(self):
        self.connection = pymysql.connect(
            host=self.host, 
            user=self.username, 
            passwd=self.password, 
            db=self.dbName, 
            connect_timeout=2,
            client_flag=CLIENT.MULTI_STATEMENTS,
            cursorclass=pymysql.cursors.DictCursor)


    def listDances(self):
        dbScript = '''
            -- ****************** SqlDBM: MySQL ******************;
            -- ***************************************************;
            -- **************************************;
            SELECT * FROM Dance ORDER BY time;
            '''    

        with self.connection.cursor() as cur:
            cur.execute("SELECT * FROM Dance ORDER BY time")
            rows = cur.fetchall()
            return rows

    def createDance(self):    
        with self.connection.cursor() as cur:
            #TODO combine these into single atomic statement?
            cur.execute("INSERT INTO Dance () VALUES ()")
            cur.execute("SELECT * FROM `Dance` where id = LAST_INSERT_ID()")
            rows = cur.fetchall()
            return rows[0]

    def resetTables(self):
        dbScript = '''
        DROP TABLE IF EXISTS Dance;
        CREATE TABLE IF NOT EXISTS `Dance`
        (
        `Id`        int NOT NULL AUTO_INCREMENT ,
        `time`      datetime DEFAULT NOW(),
        `favorite`  tinyint DEFAULT 0,
        `reviewed`  tinyint DEFAULT 0,
        `videofile` varchar(256) DEFAULT "",
        `comments`  varchar(256) DEFAULT "",

        PRIMARY KEY (`Id`)
        ) AUTO_INCREMENT=1 COMMENT='Basic information 
        about Customer';
        '''    
        with self.connection.cursor() as cur:
            cur.execute(dbScript)
