import falcon
import disco
import devices
from werkzeug.serving import run_simple
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
    if(m == None):
        return None
    d = datetime.datetime(int(m.group(1)),int(m.group(2)),int(m.group(3)),int(m.group(4)),int(m.group(5)))
    return d.strftime("%a %b %-d, %-I:%M %p")
    return f'{match.group(1)} {match.group(2)} {match.group(3)}'


class VideoListHandler():
    def __init__(self):
        pass

    def on_get(self, req, resp):
        """Handles GET requests"""

        files = os.listdir("videos")
        files.sort(reverse=True)
        files = map(lambda x: nameToDate(x),files)
        files = filter(lambda x: x != None,files)
        files = map(lambda x: f'<a href="/video/{x}">{x}</a><br>',files)
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
        resp.set_header('Content-Type', 'video/mp4')
#        log.debug(f'opening "{videoPath}"')
        stream = open(videoPath,'rb')
        size = os.path.getsize(videoPath)            
        resp.set_stream(stream,size)
        
        resp.status = falcon.HTTP_200



class AdminHandler():
    def __init__(self,deviceMgr):
        self.deviceMgr = deviceMgr

    def on_get(self, req, resp):
        """Handles GET requests"""

        resp.status = falcon.HTTP_200
        resp.text = "hello"

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

        admin = AdminHandler(deviceMgr)
        self.app.add_route('/', VideoListHandler())
        self.app.add_route('/watch/{videoName}', VideoWatchHandler())
        self.app.add_route('/video/{videoName}', VideoStreamHandler())
        self.app.add_route('/admin', admin)
        self.app.add_route('/admin/{deviceId}', admin, suffice="device")

    def start(self):
        print('Serving on port 8000...')
        print(f'video path is {os.path.join(os.path.dirname(__file__),"videos")}')
        run_simple('localhost', 8000, self.app, use_reloader=True, threaded=True,static_files={
                '/videos': os.path.join(os.path.dirname(__file__), 'videos')
            })


