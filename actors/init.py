from js9 import j
import gevent
from cloudbroker.data import Models
from cloudbroker.resourcemonitoring import resourcemonitoring

def init():
    j.portal.tools.models.cloudbroker = Models()
    from cloudbroker.healthcheck import healthcheck
    gevent.spawn(healthcheck.main)
    gevent.spawn(healthcheck.checkhealthckeck)
    gevent.spawn(resourcemonitoring.collect_stats)
