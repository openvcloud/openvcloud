#!/usr/bin/env python
import os
import sys
from js9 import j

#make sure we give cwd priority for loading modules
sys.path.insert(0, '.')

import optparse
import logging
import websocket
import websockify

try:
    from urllib.parse import parse_qs, urlparse
except:
    from cgi import parse_qs
    from urlparse import urlparse


class ProxyRequestHandler(websockify.ProxyRequestHandler):
    def get_target(self, target_cfg, path):
        """
        Parses the path, extracts a token, and looks for a valid
        target for that token in the configuration file(s). Sets
        target_host and target_port if successful
        """
        # Extract the token parameter from url
        args = parse_qs(urlparse(path)[4]) # 4 is the query from url

        if not 'token' in args or not len(args['token']):
            raise Exception("Token not present")
        token = args['token'][0].rstrip('\n')
        consoleinfo = target_cfg.cloudbroker.machine.getConsoleInfo(token=token)
        return consoleinfo['host'], consoleinfo['port']


class WebSocketProxy(websockify.WebSocketProxy):
    def __init__(self, RequestHandlerClass=ProxyRequestHandler, *args, **kwargs):
        websockify.WebSocketProxy.__init__(self, RequestHandlerClass=RequestHandlerClass, *args, **kwargs)


def websockify_init():
    websockify.logger_init()

    usage = "\n    %prog [options]"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option("--username", dest="username",
                      help="Username to authenticate with", default="admin")
    parser.add_option("--password", dest="password",
                      help="Password to authenticate with", default="admin")
    parser.add_option("--ovc-ip", dest="ovc_ip",
                      help="Ip on which OVC is running", default="localhost")
    parser.add_option("--ovc-port", dest="ovc_port",
                      help="Port on which OVC is running", default=8200)
    parser.add_option("--host", dest="listen_host",
                      help="Host to run on", default="localhost")
    parser.add_option("--port", dest="listen_port",
                      help="Port to run on", default=8091)
    parser.add_option("--web", default=None, metavar="DIR",
                      help="run webserver on same port. Serve files from DIR.")
    (opts, args) = parser.parse_args()

    try:
        opts.listen_port = int(opts.listen_port)
    except:
        parser.error("Error parsing listen port")

    try:
        opts.ovc_port = int(opts.ovc_port)
    except:
        parser.error("Error parsing ovc port")

    cl = j.clients.portal.get(ip=opts.ovc_ip, port=opts.ovc_port)
    cl.system.usermanager.authenticate(name=opts.username, secret=opts.password)
    opts.target_cfg = cl
    del opts.ovc_ip
    del opts.ovc_port
    del opts.username
    del opts.password

    # Use internal service framework
    server = WebSocketProxy(target_host=None, target_port=None, **opts.__dict__)
    server.start_server()

if __name__ == '__main__':
    websockify_init()
