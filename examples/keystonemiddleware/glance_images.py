#!/usr/bin/env python

# http://www.jamielennox.net/blog/2015/09/10/user-auth-in-openstack-services
from glanceclient import client
import json
from keystoneclient import client as ks_client
from keystoneclient import auth as ks_auth
from keystoneclient import session
from keystoneclient.auth.identity import v2, v3
from keystonemiddleware import auth_token
from oslo_config import cfg
import webob.dec
from wsgiref import simple_server
import os
import sys

CONF = cfg.CONF
CONF(project='testservice')
#print(map(lambda x: x.name, ks_auth.get_common_conf_options()))
#print(map(lambda x: x.name, ks_auth.get_plugin_options('v3password')))
v3.Password.register_conf_options(CONF, 'communication')
_vars = filter(lambda x: x[0].startswith('OS_'), os.environ.iteritems())
conf_keys = CONF.keys()
for k, v in _vars:
# Try the full var first
    n = k.lower()
    cands = (n, n[3:])
    for var in cands:
        if var in conf_keys:
            self.conf.set_default(name=var, default=v)
            break

CONF(sys.argv[1:])

# TODO: --help doesn't seem to work either way...
# Doesn't seem to matter whether keystoneclient.session.Session or keystoneauth1.session.Session
auth_args = {
    'auth_url': CONF.communication.auth_url,
    'username': CONF.communication.username,
    'password': CONF.communication.password,
    'project_name': CONF.communication.project_name,
    'project_domain_name': CONF.communication.project_domain_name
}
#auth = v3.Password(auth_args['auth_url'],**auth_args)
auth = v3.Password(**auth_args)
SESSION = session.Session(auth=auth)

@webob.dec.wsgify
def app(req):
# N.B. below does not work
# 
# DiscoveryFailure: Not enough information to determine URL. Provide either a Session, or auth_url or endpoint
# Loaded session will not set 'auth' attribute
    # TODO(kamidzi): need to pick this apart
    SESSION.auth = req.environ['keystone.token_auth']._user_auth_ref
    print(type(req.environ['keystone.token_auth']))
    for k, v in req.environ['keystone.token_auth'].iteritems():
        print('{}: {}'.format(k, type(v)))

    kclient = ks_client.Client('3', session=SESSION)
    projects = kclient.projects.list()

    # Clear the auth added above to demonstrate glanceclient 'auth' param
    session.auth = None
# TODO(kamidzi): Need to handle InvalidToken exception

    glance = client.Client('2',
                           session=SESSION,
                           auth=req.environ['keystone.token_auth'])

    resp = {
        'keystoneclient.projects': [p.name for p in projects],
        'glanceclient.images': [i.name for i in glance.images.list()],
        'keystone.token_auth.user': req.environ['keystone.token_auth'].user._data,
    }

    return webob.Response(json.dumps(resp))

if __name__ == '__main__':
    import logging
    import sys
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    logger = logging.getLogger(cfg.CONF.project)
    CONF.log_opt_values(logger, lvl=logging.INFO)

    app = auth_token.AuthProtocol(app,{})
    server = simple_server.make_server('', 8001, app)
    server.handle_request()
    server.serve_forever()
