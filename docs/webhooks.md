# Webhooks

Sometimes OVC needs to be notified with certain events from the orchestrator layer eg: when a VM is put in quarantine.
To allow communication from orchestrator to OVC, in orchestrator we created a webhook service, where you can register 
a certain webhook and the events it is interested in. When said event occurs in orchestrator, it will post to this webhook.
More about this [here](https://github.com/zero-os/0-orchestrator/blob/master/specs/webhooks.md).

Currently in OVC, the only events we are interested in are qos events, where the eventtype is `ork` and the event can be either `VM_QUARANTINE` or `VM_UNQUARANTINE`.
The api that receives events info is exposed at `/cloudbroker/qos/events`.

Whenever a new location is added in OVC, we register a new webhook service at this location with the event type we are interested in and the url to receive those events.

Snippet from the [location create](https://github.com/openvcloud/openvcloud/blob/master/actors/cloudbroker/cloudbroker__location/methodclass/cloudbroker_location.py#L79):
```python
        client = getGridClient(location, self.models)
        client.webhook.create(
            str(location.id),
            ['ork'],
            parse.urljoin(self.config['portalurl'], '/restmachine/cloudbroker/qos/events?authkey=%s' % auth_key))
```

This creates a webhook service in orchestrator with the name `location.id`, interested in event types ['ork'], specifying
that `parse.urljoin(self.config['portalurl'], '/restmachine/cloudbroker/qos/events?authkey=%s' % auth_key))` is the url orchestrator should post the events to.

