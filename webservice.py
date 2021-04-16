import flask

restService = None

class RestService:
    def __init(self,appState):
        global restService
        self.appState = appState
        restService = self

    def discotime():
        None



self.app = Flask.Flask(__name__)
self.app.config["DEBUG"] = True



@app.route('/startdiscotime', methods=['GET'])
def startDiscoTime():
    restService.discoTime()

