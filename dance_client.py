import logging
log = logging.getLogger(__name__)


class DanceClient():
    def __init__(self,remote,storage):
        self.remote = remote
        self.storage = storage
        self.endpoint = ""
        pass

    def setConfig(self,config):
            self.endpoint = config.get('endpoint',self.endpoint)

    def registerNewDance(self,id,properties = {}):
        url = f'{self.endpoint}/dance/{id}'
        log.info(f'registering new dance at {url}')
        self.remote.putRequest(url,properties)

    def registerDanceVideo(self,id,remoteVideoFilename):
        url = f'{self.endpoint}/dance/{id}'
        log.info(f'registering video at {url}')
        self.remote.putRequest(url,{"videofile":remoteVideoFilename})

    def logSonarSamples(self,id,sampleData):
        objectName = "sonar/"+id
        log.info(f'registering samples at {objectName}')
        self.storage.uploadObject(objectName,sampleData)

    def getDances(self):
        url = f'{self.endpoint}/dance'
        results = self.remote.getUrlSync(url)
        return results.json()["rows"]