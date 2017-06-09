from js9 import j
import JumpScale.grid.agentcontroller

class cloudbroker_diagnostics(object):
    """
    Operator actions to perform specific diagnostic checks on the platform
    
    """
    def __init__(self):
        self._acl = None
    
    @property
    def acl(self):
        if not self._acl:
            self._acl = j.clients.agentcontroller.get()
        return self._acl

    def checkVms(self, **kwargs):
        """
        Starts the vms check jumpscipt to do a ping to every VM from their virtual firewalls
        result boolean
        """
        return self.acl.executeJumpscript('jumpscale', 'vms_check', role='master')
