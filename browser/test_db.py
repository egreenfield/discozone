
from disco_base.discodb import DiscoDB

dbUsername = "root"#os.environ['DBUSERNAME']
dbPassword = ""#os.environ['DBPASSWORD']
dbConnection = "localhost"
dbName = "dancedb"

db = DiscoDB(username=dbUsername,password=dbPassword,connection=dbConnection,dbName=dbName)
db.connect()


db.resetTables()
row = db.createDance()
print(f'created new dance {row}')
rows = db.listDances()
print(f'rows are:{rows}')