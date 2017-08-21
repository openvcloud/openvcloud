from js9 import j
import time
import gevent
from cloudbroker.actorlib.gridmanager.client import getGridClient


class Healthcheck:
    def __init__(self):
        self.models = j.portal.tools.models.cloudbroker

    def start(self):
        while True:
            self.checkhealthckeck()
            self.fetchhealthchecks()
            gevent.sleep(30)

    def checkhealthckeck(self):
        try:
            t = time.time()
            for h in self.models.Healthcheck.objects:
                if t - h.lasttime > 2 * h.interval:
                    msg = "healthcheck %s hasn't been fired since %d seconds ago" % (h.name, t - h.lasttime)
                    eco = j.errorhandler.getErrorConditionObject(msg=msg)
                    eco.process()
                    for m in h.messages:
                        self.add_flap(m, {'status': 'EXPIRED', 'text': m.flaps[-1].text, 'lasttime': t})
                    h.save()
        except Exception as e:
            j.errorhandler.processPythonExceptionObject(e)

    def add_flap(self, m, f):
        if m.flaps:
            if m.flaps[-1].lasttime != f['lasttime']:
                if m.flaps[-1].status == f['status']:
                    m.flaps[-1].text = f['text']
                else:
                    m.flaps.append(self.models.Flap(**f))
        else:
            m.flaps.append(self.models.Flap(**f))
        m.flaps = m.flaps[-20:]

    def fetchhealthchecks(self):
        try:
            for stack in self.models.Stack.objects:
                client = getGridClient(stack.location, self.models)
                healthchecks = client.rawclient.health.ListNodeHealth(stack.referenceId).json()['healthchecks']
                for healthcheck in healthchecks:
                    h = None
                    hs = self.models.Healthcheck.find({'oid': healthcheck['id'], 'stack': stack.id})
                    if hs:
                        h = hs[0]
                    if h is None:
                        h = self.models.Healthcheck()
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
                            m = self.models.Message()
                            m.oid = message['id']
                            m.flaps = []
                            h.messages.append(m)
                        self.add_flap(m, {'status': message['status'],
                                          'text': message['text'],
                                          'lasttime': healthcheck['lasttime']})
                    moids = [m['id'] for m in healthcheck['messages']]
                    for m in h.messages:
                        if m.oid in moids:
                            continue
                        else:
                            self.add_flap(m, {'status': 'MISSING', 'text': '', 'lasttime': healthcheck['lasttime']})
                    h.save()
        except Exception as e:
            j.errorhandler.processPythonExceptionObject(e)

