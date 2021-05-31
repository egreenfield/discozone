import pymysql
from pymysql.constants import CLIENT
import logging
from pypika import MySQLQuery as Query, Table, Field


logger = logging.getLogger(__name__)



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

    def listDances(self):
        with self.connection.cursor() as cur:
            cur.execute("SELECT * FROM Dance ORDER BY time")
            rows = cur.fetchall()
            return rows

    def listDancesWithVideos(self):
        with self.connection.cursor() as cur:
            cur.execute('SELECT * FROM Dance WHERE videofile <> "" ORDER BY time')
            rows = cur.fetchall()
            return rows

    def getDanceById(self,id):
        with self.connection.cursor() as cur:
            rowCount = cur.execute(f'SELECT * FROM Dance WHERE id = {id}')
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
        print(f'executing insert string: {str(q)}')
        with self.connection.cursor() as cur:
            #TODO combine these into single atomic statement?
            cur.execute(str(q))            
            if(danceID != None):
                rowCount = cur.execute(Query.from(t).select("*").where(id == danceID).get_sql())
            else:
                rowCount = cur.execute(Query.from(t).select("*").where(id == LAST_INSERT_ID()).get_sql())
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
        print(f'executing update string: {str(q)}')
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
        for aKey in properties:
            q = q.on_duplicate_key_update(aKey,properties[aKey])
        print(f'executing insert string: {str(q)}')
        with self.connection.cursor() as cur:
            #TODO combine these into single atomic statement?
            cur.execute(str(q))            
            rowCount = cur.execute(f'SELECT * FROM `Dance` where id = {danceID}')
            if (rowCount):
                rows = cur.fetchall()
                return rows[0]
            else:    
                return None

    def resetTables(self):
        dbScript = '''

        DROP TABLE IF EXISTS Dance;
        CREATE TABLE IF NOT EXISTS `Dance`
        (
        `id`        char(36) NOT NULL ,
        `time`      datetime DEFAULT NOW(),
        `favorite`  tinyint DEFAULT 0,
        `reviewed`  tinyint DEFAULT 0,
        `videofile` varchar(256) DEFAULT "",
        `comments`  varchar(256) DEFAULT "",

        PRIMARY KEY (`Id`)
        );

        DELIMITER ;;
        CREATE TRIGGER before_insert_tablename
        BEFORE INSERT ON `Dance`
        FOR EACH ROW
        BEGIN
        IF new.id IS NULL THEN
            SET new.id = uuid();
        END IF;
        END
        ;;

        DELIMITER ;

        '''    
        with self.connection.cursor() as cur:
            cur.execute(dbScript)
