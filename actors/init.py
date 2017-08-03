def init():
    from js9 import j
    from cloudbroker.data import Models
    import gevent
    j.portal.tools.models.cloudbroker = Models()
    from cloudbroker.healthcheck import healthcheck
    gevent.Greenlet.spawn(healthcheck.main)
