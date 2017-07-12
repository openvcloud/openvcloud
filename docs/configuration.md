# Configuration

Cloudbroker config is added in the default portal config files locatted at `/optvar/cfg/portals/main/config.yaml`

We added a special section for cloudbroker.
Example:
```yaml
cloudbroker:
  portalurl: 'http://172.17.0.2:8200'
  supportemail: 'support@myorganization.org'
```

## Configuring SMTP Server

Cloudbroker sends out E-Mails when creating accounts and granting users access to certain resources.
This sections shows you how to configure your SMTP server to be able to send mails

Edit `/optvar/cfg/jumpscale9.toml`

Make sure the email section contains valid configuration

```toml
[email]
from = "info@incubaid.com"
smtp_port = 25
smtp_server = "localhost"
```