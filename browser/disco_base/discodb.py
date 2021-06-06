import pymysql
from pymysql.constants import CLIENT
import logging
from pypika import MySQLQuery as Query, Table, Field, Order


logger = logging.getLogger()
logger.setLevel(logging.INFO)


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
        self.connection.autocommit(True) 

    def listDances(self,filters={}):
        t = Table("Dance")
        q = Query.from_(t).select("*")
        logger.info(f'filters are {type(filters)} {filters}' )
        if filters == None: 
            filters = {}
        if(filters.get('hasVideo',None) == "true"):
            q = q.where(t.videofile != "")
        if(filters.get('isFavorite',None) == "true"):
            q = q.where(t.favorite == 1)
        if(filters.get('isReviewed',None) == "false"):
            q = q.where(t.reviewed == 0)
        q = q.orderby(t.time,order=Order.desc)

        with self.connection.cursor() as cur:
            cur.execute(str(q))
            rows = cur.fetchall()
            return rows

    def listDancesWithVideos(self):
        with self.connection.cursor() as cur:
            cur.execute('SELECT * FROM Dance WHERE videofile <> "" ORDER BY time')
            rows = cur.fetchall()
            return rows

    def getDanceById(self,danceID):
        t = Table("Dance")
        q = Query.from_(t).where(t.id == danceID).select("*")
        with self.connection.cursor() as cur:
            rowCount = cur.execute(str(q))
            if(rowCount > 0):
                return cur.fetchone()
            else:
                return None


    def createDance(self,danceID = None,properties = None):    
        if (properties != None):
            properties.pop("id",None)        
        t = Table("Dance")
        if(danceID == None):
            q = Query.into(t).columns(*properties.keys()).insert(*properties.values())
        else:
            q = Query.into(t).columns("id",*properties.keys()).insert(danceID,*properties.values())
        logger.debug(f'executing insert string: {str(q)}')
        with self.connection.cursor() as cur:
            #TODO combine these into single atomic statement?
            cur.execute(str(q))            
            if(danceID != None):
                rowCount = cur.execute(Query.from_(t).select("*").where(id == danceID).get_sql())
            else:
                rowCount = cur.execute(Query.from_(t).select("*").where(id == LAST_INSERT_ID()).get_sql())
            if (rowCount):
                rows = cur.fetchall()
                return rows[0]
            else:    
                return None

        with self.connection.cursor() as cur:
            #TODO combine these into single atomic statement?
            cur.execute(f'INSERT INTO `Dance` () VALUES ()')            
            cur.execute("SELECT * FROM `Dance` where id = LAST_INSERT_ID()")
            rows = cur.fetchall()
            return rows[0]

    def updateDance(self,danceID,properties):

        properties.pop("id",None)
        t = Table("Dance")
        q = Query.update(t)
        for aKey in properties:
            q = q.set(aKey,properties[aKey])
        q = q.where(t.id == danceID)
        logger.debug(f'executing update string: {str(q)}')
        with self.connection.cursor() as cur:
            #TODO combine these into single atomic statement?
            cur.execute(str(q))            
            rowCount = cur.execute(f'SELECT * FROM `Dance` where id = {danceID}')
            if (rowCount):
                rows = cur.fetchall()
                return rows[0]
            else:    
                return None

    def upsertDance(self,danceID,properties):

        properties.pop("id",None)        
        t = Table("Dance")
        q = Query.into(t).columns("id",*properties.keys()).insert(danceID,*properties.values())
        q = q.on_duplicate_key_update("id",danceID)
        for aKey in properties:
            q = q.on_duplicate_key_update(aKey,properties[aKey])
        with self.connection.cursor() as cur:
            #TODO combine these into single atomic statement?
            logger.info(f'executing insert string: {str(q)}')
            cur.execute(str(q))          
            q = Query.from_(t).select('*').where(t.id == danceID)
            logger.info(f'executing {str(q)}')  
            rowCount = cur.execute(str(q))
            if (rowCount):
                rows = cur.fetchall()
                return rows[0]
            else:    
                return None

    def deleteDance(self,danceID):

        t = Table("Dance")
        q = Query.from_(t).where(t.id == danceID).delete()
        with self.connection.cursor() as cur:
            logger.info(f'executing delete string: {str(q)}')
            rowCount = cur.execute(str(q))          
            return 0 if rowCount > 0 else -1

    def resetTables(self):
        dbScript = '''

use dancedb;

        DROP TABLE IF EXISTS `Dance`;
        CREATE TABLE IF NOT EXISTS `Dance`
        (
        `id`        char(36) DEFAULT "" NOT NULL ,
        `time`      datetime DEFAULT NOW(),
        `favorite`  tinyint DEFAULT 0,
        `reviewed`  tinyint DEFAULT 0,
        `videofile` varchar(256) DEFAULT "",
        `comments`  varchar(256) DEFAULT "",
        `song`      varchar(256) DEFAULT "",

        PRIMARY KEY (`Id`)
        );

        DELIMITER ;;
        CREATE TRIGGER before_insert_tablename
        BEFORE INSERT ON `Dance`
        FOR EACH ROW
        BEGIN
        IF new.id = "" THEN
            SET new.id = uuid();
        END IF;
        END
        ;;

        DELIMITER ;
        '''    
        with self.connection.cursor() as cur:
            cur.execute(dbScript)
