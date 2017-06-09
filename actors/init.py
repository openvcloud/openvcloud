def init():
    from js9 import j
    from cloudbroker.data import Models
    j.portal.tools.models.cloudbroker = Models()
