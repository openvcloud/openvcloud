from js9 import j
from JumpScale9Portal.portal import exceptions
from cloudbroker.data.models import to_python
from cloudbroker.actorlib import authenticator
from cloudbroker.actorlib.baseactor import BaseActor
import netaddr


class cloudapi_portforwarding(BaseActor):

    """
    Portforwarding api

    """

    def __init__(self):
        super(cloudapi_portforwarding, self).__init__()
        self.netmgr = self.cb.netmgr

    def _getLocalIp(self, machine):
        for nic in machine.nics:
            if nic.type == 'vxlan':
                return nic.ipAddress
        return None

    @authenticator.auth(acl={'cloudspace': set('C')})
    def create(self, cloudspaceId, publicIp, publicPort, machineId, localPort, protocol=None, **kwargs):
        """
        Create a port forwarding rule

        :param cloudspaceId: id of the cloudspace
        :param publicIp: public ipaddress
        :param publicPort: public port
        :param machineId: id of the virtual machine
        :param localPort: local port on vm
        :param protocol: protocol udp or tcp
        """
        machine = self.models.VMachine.get(machineId)
        protocol = protocol or 'tcp'

        if publicPort > 65535 or publicPort < 1:
            raise exceptions.BadRequest("Public port should be between 1 and 65535")
        if localPort > 65535 or localPort < 1:
            raise exceptions.BadRequest("Local port should be between 1 and 65535")
        if protocol and protocol not in ('tcp', 'udp'):
            raise exceptions.BadRequest("Protocol should be either tcp or udp")
        if machine.cloudspace.status != 'DEPLOYED':
            raise exceptions.BadRequest("Cannot create a portforwarding during cloudspace deployment.")

        try:
            publicIp = str(netaddr.IPNetwork(publicIp).ip)
        except netaddr.AddrFormatError:
            raise exceptions.BadRequest("Invalid public IP %s" % publicIp)

        if machine.cloudspace.externalnetworkip.split('/')[0] != publicIp:
            raise exceptions.BadRequest("Invalid public IP %s" % publicIp)

        localIp = self._getLocalIp(machine)
        if localIp is None:
            raise exceptions.NotFound('Cannot create portforwarding when Virtual Machine did not acquire an IP Address.')

        if self._selfcheckduplicate(machine.cloudspace, publicIp, publicPort, protocol):
            raise exceptions.Conflict("Forward to %s with port %s already exists" % (publicIp, publicPort))
        forward = self.models.ForwardRule(
            fromAddr=publicIp,
            fromPort=publicPort,
            toAddr=localIp,
            toPort=localPort,
            protocol=protocol
        )
        machine.cloudspace.modify(push__forwardRules=forward)
        self.cb.netmgr.update(machine.cloudspace)
        return True

    def deleteByVM(self, machine, **kwargs):
        def getIP():
            for nic in machine.nics:
                if nic.ipAddress != 'Undefined':
                    return nic.ipAddress
            return None
        localIp = getIP()
        if localIp is None:
            return True
        machine.cloudspace.modify(pull__forwardRules={'toAddr': localIp})
        self.cb.netmgr.update(machine.cloudspace)
        return True

    def _selfcheckduplicate(self, cloudspace, publicIp, publicPort, protocol):
        for rule in cloudspace.forwardRules:
            if rule.fromAddr == publicIp and rule.fromPort == publicPort and rule.protocol == protocol:
                return True
        return False

    @authenticator.auth(acl={'cloudspace': set('X')})
    def delete(self, cloudspaceId, id, **kwargs):
        """
        Delete a specific port forwarding rule

        :param cloudspaceId: id of the cloudspace
        :param id: id of the port forward rule

        """
        cloudspace = self.models.cloudspace.get(cloudspaceId)
        forward = cloudspace.forwardRules.pop(id, None)
        if not forward:
            raise exceptions.NotFound('Cannot find the rule with id %s' % str(id))
        self.models.cloudspace.updateSearch({'id': cloudspaceId},
                                            {'$pull': {'forwardRules': forward}})
        self.cb.netmgr.update(cloudspace)
        return True

    @authenticator.auth(acl={'cloudspace': set('X')})
    def deleteByPort(self, cloudspaceId, publicIp, publicPort, proto=None, **kwargs):
        """
        Delete a specific port forwarding rule by public port details

        :param cloudspaceId: id of the cloudspace
        :param publicIp: port forwarding public ip
        :param publicPort: port forwarding public port
        :param proto: port forwarding protocol
        """
        cloudspace = self.models.Cloudspace.get(cloudspaceId)
        forward = {'fromAddr': publicIp,
                   'fromPort': publicPort}
        if proto:
            forward['protocol'] = proto
        cloudspace.modify(pull__forwardRules=forward)
        self.cb.netmgr.update(cloudspace)
        return True

    @authenticator.auth(acl={'cloudspace': set('C')})
    def update(self, cloudspaceId, id, publicIp, publicPort, machineId, localPort, protocol, **kwargs):
        """
        Update a port forwarding rule

        :param cloudspaceId: id of the cloudspace
        :param id: id of the portforward to edit
        :param publicIp: public ipaddress
        :param publicPort: public port
        :param machineId: id of the virtual machine
        :param localPort: local port
        :param protocol: protocol udp or tcp
        """
        machineId = int(machineId)
        cloudspaceId = int(cloudspaceId)
        cloudspace = self.models.cloudspace.get(cloudspaceId)
        forwards = cloudspace.forwardRules
        id = int(id)
        forward = forwards.pop(id, None)
        if not forward:
            raise exceptions.NotFound('Cannot find the rule with id %s' % str(id))
        machine = self.models.vmachine.get(machineId)
        if machine.nics:
            if machine.nics[0].ipAddress != 'Undefined':
                localIp = machine.nics[0].ipAddress
            else:
                raise exceptions.NotFound('No correct ipaddress found for machine with id %s' % machineId)
        if self._selfcheckduplicate(cloudspace, publicIp, publicPort, protocol):
            raise exceptions.Conflict("Forward for %s with port %s already exists" % (publicIp, publicPort))
        self.models.cloudspace.updateSearch({'id': cloudspace.id},
                                            {'$pull': {'forwardRules': {'fromAddr': forward['fromAddr'],
                                                                        'fromPort': forward['fromPort']}}})
        forward['fromAddr'] = publicIp
        forward['fromPort'] = publicPort
        forward['toAddr'] = localIp
        forward['toPort'] = localPort
        forward['protocol'] = protocol
        self.netmgr.update(cloudspace)
        self.models.cloudspace.updateSearch({'id': cloudspace.id},
                                            {'$push': {'forwardRules': forward}})
        return self._process_list(cloudspace.forwardRules, cloudspaceId)

    def _process_list(self, forwards, cloudspace):
        result = list()
        machines = self.models.VMachine.objects(cloudspace=cloudspace, status__nin=['DESTROYED', 'ERROR']).only('nics', 'name', 'id')

        def getMachineByIP(ip):
            for machine in machines:
                for nic in machine.nics:
                    if nic.ipAddress == ip:
                        return machine

        for index, forward in enumerate(forwards):
            f = to_python(forward)
            f['id'] = index
            f['publicIp'] = f.pop('fromAddr')
            f['publicPort'] = f.pop('fromPort')
            f['localPort'] = f.pop('toPort')
            machine = getMachineByIP(forward.toAddr)
            if machine is None:
                f['machineName'] = forward.toAddr
            else:
                f['machineName'] = "%s (%s)" % (machine.name, forward.toAddr)
                f['machineId'] = str(machine.id)
            if not f['protocol']:
                f['protocol'] = 'tcp'
            result.append(f)
        return result

    @authenticator.auth(acl={'cloudspace': set('R'), 'machine': set('R')})
    def list(self, cloudspaceId, machineId=None, **kwargs):
        """
        List all port forwarding rules in a cloudspace or machine

        :param cloudspaceId: id of the cloudspace
        :param machineId: id of the machine, all rules of cloudspace will be listed if set to None
        """
        machine = None
        if machineId:
            machine = self.models.VMachine.get(machineId)
            cloudspace = machine.cloudspace
        else:
            cloudspace = self.models.Cloudspace.get(cloudspaceId)

        def getIP():
            if machine:
                for nic in machine.nics:
                    if nic.type == 'vxlan':
                        return nic.ipAddress
            return None

        forwards = cloudspace.forwardRules
        if machine:
            localip = getIP()
            forwards = filter(lambda fw: fw.toAddr == localip, forwards)

        return self._process_list(forwards, cloudspace)

    def listcommonports(self, **kwargs):
        """
        List a range of predifined ports
        """
        return [{'name': 'http', 'port': 80, 'protocol': 'tcp'},
                {'name': 'https', 'port': 443, 'protocol': 'tcp'},
                {'name': 'ftp', 'port': 21, 'protocol': 'tcp'},
                {'name': 'ssh', 'port': 22, 'protocol': 'tcp'}]
