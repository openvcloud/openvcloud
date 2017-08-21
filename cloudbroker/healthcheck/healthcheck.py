from js9 import j
import time
from cloudbroker.actorlib.gridmanager.client import getGridClient
from gevent import Greenlet
models = j.portal.tools.models.cloudbroker


def checkhealthckeck():
    try:
        hs = models.Healthcheck.objects.all()
        t = time.time()
        for h in hs:
            if t - h.lasttime > 2 * h.interval:
                eco = j.errorhandler.getErrorConditionObject(msg="healthcheck %s hasn't been fired since %d seconds ago" % (h.name, t - h.lasttime))
                eco.process()
    except Exception as e:
        j.errorhandler.processPythonExceptionObject(e)
    g = Greenlet(checkhealthckeck)
    g.start_later(30)


def main():
    try:
        stacks = models.Stack.find({})
        for stack in stacks:
            client = getGridClient(stack.location, models)
            healthchecks = client.rawclient.health.ListNodeHealth(stack.referenceId).json()['healthchecks']
            for healthcheck in healthchecks:
                h = None
                hs = models.Healthcheck.find({'oid': healthcheck['id'], 'stack': stack.id})
                if hs:
                    h = hs[0]
                if h is None:
                    h = models.Healthcheck()
                    h.oid = healthcheck['id']
                    h.stack = stack
                h.name = healthcheck['name']
                h.resource = healthcheck['resource']
                h.category = healthcheck['category']
                h.lasttime = healthcheck['lasttime']
                h.interval = healthcheck['interval']
                h.stacktrace = healthcheck['stacktrace']
                for message in healthcheck['messages']:
                    m = None
                    if h.messages:
                        ms = [mes for mes in h.messages if mes.oid == message['id']]
                        if ms:
                            m = ms[0]
                    if m is None:
                        m = models.Message()
                        m.oid = message['id']
                        m.flaps = []
                        h.messages.append(m)
                    add_flap(m, {'status': message['status'], 'text': message['text'], 'lasttime': healthcheck['lasttime']})
                moids = [m['id'] for m in healthcheck['messages']]
                for m in h.messages:
                    if m.oid in moids:
                        continue
                    else:
                        add_flap(m, {'status': 'MISSING', 'text': '', 'lasttime': healthcheck['lasttime']})
                h.save()
    except Exception as e:
        j.errorhandler.processPythonExceptionObject(e)
    g = Greenlet(main)
    g.start_later(30)


def add_flap(m, f):
    if m.flaps:
        if m.flaps[-1].lasttime != f['lasttime']:
            if m.flaps[-1].status == f['status']:
                m.flaps[-1].text = f['text']
            else:
                m.flaps.append(models.Flap(**f))
    else:
        m.flaps.append(models.Flap(**f))
    m.flaps = m.flaps[-20:]
