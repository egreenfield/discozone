import requests
from  concurrent.futures import ThreadPoolExecutor

class Remote:
    def __init__(self):
        self.remotePool = ThreadPoolExecutor(max_workers=10)

    @staticmethod
    def handleRequest(url):
        print(f'fetching {url}')
        requests.get(url)

    def request(self,url):
        self.remotePool.submit(Remote.handleRequest,url)
