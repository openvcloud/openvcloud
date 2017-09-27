from .base import BaseManager
from requests import exceptions


class MachineManager(BaseManager):
    def create(self, machine, disks, nodeId):
        data = self.get_machine_model(machine, disks)
        self.client.nodes.CreateVM(data, nodeId)
        machine.referenceId = data['id']

    def get_machine_model(self, machine, disks=None):
        data_disks = list()
        data_nics = list()

        for nic in machine.nics:
            data_nics.append({'id': str(nic.networkId),
                              'type': nic.type,
                              'macaddress': nic.macAddress
                              })

        if disks is None:
            disks = machine.disks
        for disk in disks:
            _, volId = disk.referenceId.split(':')
            data_disks.append({'maxIOps': disk.iops,
                               'vdiskid': volId
                               })

        vmid = 'vm-{}'.format(machine.id)
        data = {'id': vmid,
                'memory': machine.memory,
                'cpu': machine.vcpus,
                'nics': data_nics,
                'disks': data_disks,
                }
        return data

    def update(self, machine, nodeId):
        data = self.get_machine_model(machine)
        return self.client.nodes.UpdateVM(vmid=data['id'], nodeid=nodeId, data=data)

    def get(self, machineId, nodeId):
        return self.client.nodes.GetVM(nodeid=nodeId, vmid='vm-{}'.format(machineId)).json()

    def start(self, machineId, nodeId):
        self.client.nodes.StartVM({}, nodeid=nodeId, vmid='vm-{}'.format(machineId))

    def stop(self, machineId, nodeId):
        self.client.nodes.StopVM({}, nodeid=nodeId, vmid='vm-{}'.format(machineId))

    def shutdown(self, machineId, nodeId):
        self.client.nodes.ShutdownVM({}, nodeid=nodeId, vmid='vm-{}'.format(machineId))

    def pause(self, machineId, nodeId):
        self.client.nodes.PauseVM({}, nodeid=nodeId, vmid='vm-{}'.format(machineId))

    def resume(self, machineId, nodeId):
        self.client.nodes.ResumeVM({}, nodeid=nodeId, vmid='vm-{}'.format(machineId))

    def status(self, machineId, nodeId):
        return self.client.nodes.GetVM(nodeid=nodeId, vmid='vm-{}'.format(machineId)).json()['status']

    def destroy(self, machineId, nodeId):
        try:
            return self.client.nodes.DeleteVM(nodeid=nodeId, vmid='vm-{}'.format(machineId))
        except exceptions.HTTPError as e:
            if e.response.status_code != 404:
                raise
