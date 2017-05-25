#!/usr/bin/env python

# http://www.jamielennox.net/blog/2015/09/10/user-auth-in-openstack-services
from glanceclient import client
from keystoneclient.auth.identity import v2, v3
from keystoneclient import auth as ks_auth
from keystoneclient import client as ks_client
from keystoneclient import session
from keystonemiddleware import auth_token
from oslo_config import cfg
from wsgiref import simple_server
import json
import logging
import os
import sys
import webob.dec

CONF = cfg.CONF
CONF(project='testservice')
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
    'user_domain_name': CONF.communication.user_domain_name,
    'project_domain_name': CONF.communication.project_domain_name
}

AUTH = v3.Password(**auth_args)
SESSION = session.Session(auth=AUTH)

@webob.dec.wsgify
def app(req):
    supplied_auth = None
    try:
        #<class 'keystonemiddleware.auth_token._user_plugin.UserAuthPlugin'>
        supplied_auth = req.environ['keystone.token_auth'] #._auth
        # Can also use _auth attribute that will be Identity Plugin
    except AttributeError, e:
        for k, v in req.environ['keystone.token_auth'].__dict__.iteritems():
            print('{}: {}'.format(k, type(v)))

    # Use orignal session, with original auth information
    kclient = ks_client.Client('3', session=SESSION)
    projects = kclient.projects.list()

    # TODO(kamidzi): Need to handle InvalidToken exception
    # Now use supplied auth credentials
    glance = client.Client('2',
                           session=SESSION,
                           auth=supplied_auth)
    images = glance.images.list()
    resp = {
        'keystoneclient.projects': [p.name for p in projects],
        'glanceclient.images': [i.name for i in images],
        'keystone.token_auth.user': req.environ['keystone.token_auth'].user._data,
    }

    return webob.Response(json.dumps(resp, indent=2))

if __name__ == '__main__':
    import logging
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    logger = logging.getLogger(cfg.CONF.project)
    CONF.log_opt_values(logger, lvl=logging.INFO)

    app = auth_token.AuthProtocol(app,{})
    server = simple_server.make_server('', 8001, app)
    server.serve_forever()
