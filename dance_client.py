import logging
log = logging.getLogger(__name__)


class DanceClient():
    def __init__(self,remote):
        self.remote = remote
        self.endpoint = ""
        pass
    
    def setConfig(self,config):
            self.endpoint = config.get('endpoint',self.endpoint)

    def registerNewDance(self,id):
        url = f'{self.endpoint}/dance/{id}'
        log.info(f'registering new dance at {url}')
        self.remote.putRequest(url,{})

