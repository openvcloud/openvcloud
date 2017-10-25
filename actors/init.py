from js9 import j
import gevent
from cloudbroker.data import Models
from cloudbroker.resourcemonitoring import resourcemonitoring
from cloudbroker.healthcheck import healthcheck


def init():

    # defining the persmission level groups if they are not created already
    requiredLevels = {'level1', 'level2', 'level3'}
    for group in j.portal.tools.models.system.Group.objects(name__startswith='level'):
        if group.name in requiredLevels:
            requiredLevels.remove(group.name)
    for level in requiredLevels:
        levelGroup = j.portal.tools.models.system.Group(name=level)
        levelGroup.save()

    # hooking the cloudbroker database(models) to j
    j.portal.tools.models.cloudbroker = Models()

    # spawning the health checks and the stats collector(this should be move to orchestrator)
    health = healthcheck.Healthcheck()
    gevent.spawn(health.start)
    gevent.spawn(resourcemonitoring.collect_stats)
