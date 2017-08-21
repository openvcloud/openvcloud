from js9 import j
import gevent
from cloudbroker.data import Models
from cloudbroker.resourcemonitoring import resourcemonitoring
from cloudbroker.healthcheck import healthcheck


def init():
    j.portal.tools.models.cloudbroker = Models()
    health = healthcheck.Healthcheck()
    gevent.spawn(health.start)
    gevent.spawn(resourcemonitoring.collect_stats)
