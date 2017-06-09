from .base import BaseManager


class NetworkManager(BaseManager):
    def createBridge(self, nodeId, nic):
        bridge = {'name': 'vx-{:04x}'.format(nic.networkId),
                  'networkMode': 'openvswitch',
                  'nat': False,
                  'settings': {'parent': 'vxbackend', 'vxlanid': nic.networkId}
                  }
        nic.referenceId = self.client.node.CreateBridge(bridge, nodeId).json()
