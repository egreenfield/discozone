import falcon
import disco
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
        

class RestService:
    def __init__(self,machine,device):
        self.machine = machine
        self.app = falcon.App()

        self.app.add_route('/start', RemoteEvent(disco.Events.RemoteStart,machine))
        self.app.add_route('/stop', RemoteEvent(disco.Events.RemoteStop,machine))

        self.app.add_route('/event/{eventName}', WebEventHandler(device))

    def start(self):
        with make_server('', 8000, self.app) as httpd:
            print('Serving on port 8000...')

            # Serve until process is killed
            httpd.serve_forever()


