import requests
import json
import logging
log = logging.getLogger(__name__)

from  concurrent.futures import ThreadPoolExecutor

class Remote:
    def __init__(self):
        self.remotePool = ThreadPoolExecutor(max_workers=10)

    @staticmethod
    def getRequest(url):
        log.debug(f'getting {url}')
        requests.get(url)

    @staticmethod
    def postRequest(url,body):
        log.debug(f'posting {url} with body {body}')
        headers = {"Content-Type": "application/json"}        
        requests.post(url,data = body,headers=headers)

    @staticmethod
    def putRequest(url,body):
        log.debug(f'putting {url} with body {body}')
        headers = {"Content-Type": "application/json"}        
        requests.put(url,json = body,headers=headers)

    def getUrl(self,url):
        self.remotePool.submit(Remote.getRequest,url)

    def postUrl(self,url,body = {}):
        self.remotePool.submit(Remote.postRequest,url,json.dumps(body))

    def putUrl(self,url,body = {}):
        self.remotePool.submit(Remote.putRequest,url,json.dumps(body))
