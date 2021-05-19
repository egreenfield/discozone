import falcon
import disco
import devices
from wsgiref.simple_server import make_server
import io
import os
import re
import datetime


from functools import reduce

import logging
log = logging.getLogger(__name__)



class RemoteEvent:
    def __init__(self,event,machine):
        self.event = event
        self.machine = machine

    def on_get(self, req, resp):
        """Handles GET requests"""
        resp.status = falcon.HTTP_200  # This is the default status
        resp.text = ('{}')
        self.machine.addEvent(self.event)        


class WebEventHandler():
    def __init__(self,device):
        self.device = device

    def on_get(self, req, resp,eventName):
        """Handles GET requests"""
        resp.status = falcon.HTTP_200  # This is the default status
        resp.text = ('{}')
        self.device.raiseEvent(eventName)            
        
class WebCommandHandler():
    def __init__(self,deviceMgr):
        self.deviceMgr = deviceMgr

    def on_get(self, req, resp,deviceClass,deviceId,commandName):
        """Handles GET requests"""
        resp.status = falcon.HTTP_200  # This is the default status
        resp.text = ('{}')
        self.deviceMgr.execRemoteCommand(deviceClass,commandName,deviceId)           


def nameToDate(name):
    m = re.search(r"(\d*)_(\d*)_(\d*)_(\d*)_(\d*)_(\d*)",name)
    d = datetime.datetime(int(m.group(1)),int(m.group(2)),int(m.group(3)),int(m.group(4)),int(m.group(5)))
    return d.strftime("%a %b %-d, %-I:%M %p")
    return f'{match.group(1)} {match.group(2)} {match.group(3)}'


class VideoListHandler():
    def __init__(self):
        pass

    def on_get(self, req, resp):
        """Handles GET requests"""
        resp.status = falcon.HTTP_200  # This is the default status
        resp.text = ('{}')

        files = os.listdir("videos")
        files.sort(reverse=True)
        files = map(lambda x: f'<a href="/video/{x}">{nameToDate(x)}</a><br>',files)
        result = reduce(lambda a,b:a+b,files,"")

        resp.status = falcon.HTTP_200  
        resp.content_type = falcon.MEDIA_HTML
        resp.text = result

class VideoWatchHandler():
    def __init__(self):
        pass

    def on_get(self, req, resp,videoName):
        """Handles GET requests"""

        resp.status = falcon.HTTP_200  
        resp.content_type = falcon.MEDIA_HTML
        resp.text = f'''<video controls>
                            <source src="/video/{videoName}" type="video/mp4">
                            Your browser does not support the video tag.
                        </video>
                        '''        
class VideoStreamHandler():
    def __init__(self):
        pass

    def on_get(self, req, resp,videoName):
        """Handles GET requests"""

        videoPath = os.path.join("videos", videoName)
        if not os.path.exists(videoPath):
            log.debug(f'can\'t find {videoPath}')

        # resp.stream = io.open(videoPath, 'rb')
        # resp.content_length = os.path.getsize(videoPath)
        # log.debug(f'content length is {resp.content_length}')
        # resp.content_type = "video/h264"

        # media = 'test.mp4'
        resp.set_header('Content-Type', 'video/mp4')
        log.debug(f'opening "{videoPath}"')
        stream = open(videoPath,'rb')
        size = os.path.getsize(videoPath)            
        #resp.content_length = size
        resp.set_stream(stream,size)
        #resp.body = stream.read(size)
        
        


        resp.status = falcon.HTTP_200  # This is the default status
#        resp.text = ('{}')

class RestService:
    def __init__(self,machine,deviceMgr):
        self.machine = machine
        self.app = falcon.App()

        self.app.add_route('/start', RemoteEvent(disco.Events.RemoteStart,machine))
        self.app.add_route('/stop', RemoteEvent(disco.Events.RemoteStop,machine))

        webDevice = devices.Device()
        webDevice.setClass("api")
        deviceMgr.addDevice(webDevice)
        self.app.add_route('/event/{eventName}', WebEventHandler(webDevice))

        self.app.add_route('/command/{deviceClass}/{deviceId}/{commandName}', WebCommandHandler(deviceMgr))

        self.app.add_route('/', VideoListHandler())
        self.app.add_route('/watch/{videoName}', VideoWatchHandler())
        self.app.add_route('/video/{videoName}', VideoStreamHandler())

    def start(self):
        with make_server('', 8000, self.app) as httpd:
            print('Serving on port 8000...')

            # Serve until process is killed
            httpd.serve_forever()


