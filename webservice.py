import falcon
import disco
import devices
from wsgiref.simple_server import make_server




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


class RestService:
    def __init__(self,machine,deviceMgr):
        self.machine = machine
        self.app = falcon.App()

        self.app.add_route('/start', RemoteEvent(disco.Events.RemoteStart,machine))
        self.app.add_route('/stop', RemoteEvent(disco.Events.RemoteStop,machine))

        webDevice = devices.Device()
        deviceMgr.addDevice("api",webDevice)
        self.app.add_route('/event/{eventName}', WebEventHandler(webDevice))

        self.app.add_route('/command/{deviceClass}/{deviceId}/{commandName}', WebCommandHandler(deviceMgr))

    def start(self):
        with make_server('', 8000, self.app) as httpd:
            print('Serving on port 8000...')

            # Serve until process is killed
            httpd.serve_forever()


