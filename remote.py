import requests
from  concurrent.futures import ThreadPoolExecutor

class Remote:
    def __init__(self):
        self.remotePool = ThreadPoolExecutor(max_workers=10)

    @staticmethod
    def getRequest(url):
        print(f'fetching {url}')
        requests.get(url)

    @staticmethod
    def postRequest(url,body):
        print(f'fetching {url}')
        requests.post(url,data = body)

    def getUrl(self,url):
        self.remotePool.submit(Remote.getRequest,url)

    def postUrl(self,url,body):
        self.remotePool.submit(Remote.postRequest,url,body)
