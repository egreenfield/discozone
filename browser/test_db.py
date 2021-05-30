
from disco_base.discodb import DiscoDB
import logging

dbUsername = "root"#os.environ['DBUSERNAME']
dbPassword = ""#os.environ['DBPASSWORD']
dbConnection = "localhost"
dbName = "dancedb"

db = DiscoDB(username=dbUsername,password=dbPassword,host=dbConnection,dbName=dbName)
db.connect()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

db.resetTables()
row = db.createDance()
print(f'created new dance {row}')
rows = db.listDances()
print(f'rows are:{rows}')
dance = db.getDanceById(row['Id'])
print(f'get returned {dance}')
dance = db.updateDance(row['Id'],{"comments":"updated"})
print(f'get returned {dance}')