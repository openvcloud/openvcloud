# Configuration

Cloudbroker config is added in the default portal config files located at `~/js9host/cfg/jumpscale9.toml`.

We added a special section for cloudbroker.
Example:
```toml
[portal.main.cloudbroker]
portalurl = "http://172.17.0.2:8200"
supportemail = "support@myorganization.org"
```

## Configuring SMTP Server

Cloudbroker sends out E-Mails when creating accounts and granting users access to certain resources.
This sections shows you how to configure your SMTP server to be able to send mails

Make sure the email section contains valid configuration

```python
data = {'from': 'info@gig.tech', 'smtp_port': 25, 'smtp_server': 'localhost'}
j.clients.email.get(instance='main', data=data, create=True, die=True, interactive=False)
```
