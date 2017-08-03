def init():
    from js9 import j
    from cloudbroker.data import Models
    import gevent
    from cloudbroker.healthcheck import healthcheck
    j.portal.tools.models.cloudbroker = Models()
    gevent.Greenlet.spawn(healthcheck.main)
