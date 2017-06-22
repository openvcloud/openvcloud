from .storage import StorageManager
from .net import NetworkManager
from .machine import MachineManager
from zeroos.orchestrator.client import APIClient
import requests

gridclients = {}


def refresh_jwt_token(token):
    headers = {'Authorization': 'bearer {}'.format(token)}
    resp = requests.get('https://itsyou.online/v1/oauth/jwt/refresh', headers=headers)
    return resp.content.decode()


class GridClient(object):
    def __init__(self, location, models):
        self.rawclient = APIClient(location.apiUrl.rstrip('/'))
        if location.apiToken:
            self.rawclient.set_auth_header('Bearer {}'.format(location.apiToken))

            def refresh_token(r, *args, **kwargs):
                request = r.request
                if r.status_code == 440 and not hasattr(request, 'isretry'):
                    newtoken = refresh_token(location.apiToken)
                    location.update(apiToken=newtoken)
                    self.rawclient.set_auth_header('Bearer {}'.format(location.apiToken))
                    request.headers['Authorization'] = 'Beater {}'.format(location.apiToken)
                    request.isretry = True
                    return self.rawclient.send(request)

            self.rawclient.session.hooks['response'] = refresh_token

        self.models = models
        self._network = None
        self._storage = None
        self._machine = None

    @property
    def network(self):
        if not self._network:
            self._network = NetworkManager(self.rawclient, self.models)
        return self._network

    @property
    def machine(self):
        if not self._machine:
            self._machine = MachineManager(self.rawclient, self.models)
        return self._machine

    @property
    def storage(self):
        if not self._storage:
            self._storage = StorageManager(self.rawclient, self.models)
        return self._storage

    def getActiveNodes(self):
        nodes = self.getNodes()
        active = [node for (node, state) in nodes if state]
        return active

    def getNodes(self):
        nodes = self.rawclient.nodes.ListNodes().json()
        return [(node, node['status'] == 'running') for node in nodes]

    def getNode(self, nodeid):
        return self.rawclient.nodes.GetNode(nodeid).json()


class BaseManager(object):
    def __init__(self, client, models):
        self.client = client
        self.models = models


def getGridClient(location, models):
    """
    Get gridclient from gid
    """
    if location.id not in gridclients:
        gridclients[location.id] = GridClient(location, models)
    return gridclients[location.id]
