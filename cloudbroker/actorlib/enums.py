class MachineStatus(object):
    _ENUMS = {'vxlan': {'running': 'RUNNING',
                        'halted': 'HALTED',
                        'starting': 'STARTING',
                        'paused': 'PAUSED',
                        'halting': 'HALTING',
                        'migrating': 'MIGRATING'}}

    @classmethod
    def _init(cls):
        for enum in cls._ENUMS['vxlan']:
            setattr(cls, enum, cls._ENUMS['vxlan'][enum])


MachineStatus._init()
