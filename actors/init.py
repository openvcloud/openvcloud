def init():
    from js9 import j
    import gevent
    from cloudbroker.data import Models
    j.portal.tools.models.cloudbroker = Models()

    from cloudbroker.healthcheck import healthcheck
    gevent.Greenlet.spawn(healthcheck.main)

    from cloudbroker.resourcemonitoring import resourcemonitoring
    gevent.Greenlet.spawn(resourcemonitoring.collect_stats)
