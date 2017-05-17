#!/usr/bin/env python
from keystoneclient.v3 import client
from keystoneclient import auth as ks_auth
from keystoneclient import session
from keystoneclient.auth.identity import v3
from os import environ
import os
import sys
try:
    import simplejson as json
except ImportError:
    import json

username = environ.get('OS_USERNAME')
auth_args = {
        'user_domain_name': environ.get('OS_USER_DOMAIN_NAME'),
        'project_domain_name': environ.get('OS_PROJECT_DOMAIN_NAME'),
        'project_name': environ.get('OS_PROJECT_NAME'),
        'auth_url': environ.get('OS_AUTH_URL'),
        'password': environ.get('OS_PASSWORD'),
        'username': username,
}

try:
    token = sys.argv[1]
except IndexError:
    sys.exit('Must supply token as first argument.')

auth = v3.Password(**auth_args)
sess = session.Session(auth=auth)
ks = client.Client(session=sess)

print(ks.tokens.validate(token))
