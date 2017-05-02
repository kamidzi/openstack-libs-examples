#!/usr/bin/env python
# https://chrigl.de/posts/2014/08/27/oslo-messaging-example.html
# coding: utf-8
from oslo_config import cfg
import oslo_messaging as messaging
import logging
import sys

logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.INFO)


def configure_options():
    return cfg.CONF

if __name__ == '__main__':
    conf = configure_options()
    #NOTE(kamidzi): need to use cfg.CONF not local ConfigOpts to work..
    conf(sys.argv[1:])
    #conf.log_opt_values(log, logging.INFO)

    method_name = 'get_transport'
    #method_name = 'get_notification_transport'
    #transport = messaging.get_notification_transport(conf, transport_url)
    #transport = messaging.get_transport(conf, transport_url)
    transport_factory_method = getattr(messaging, method_name)
    transport = transport_factory_method(conf)#, transport_url)

    driver = 'messaging'
    notifier = messaging.Notifier(transport,
                                  driver=driver,
                                  publisher_id='testing',
                                  topics=['monitor'])
    notifier.info({'some': 'context'}, 'just.testing', {'heavy': 'payload'})
