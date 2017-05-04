#!/usr/bin/env python
# coding: utf-8
from oslo_config import cfg
import oslo_messaging as messaging
import logging
import eventlet
import sys


class NotificationHandler(object):
    def info(self, ctxt, publisher_id, event_type, payload, metadata):
        if publisher_id == 'testing':
            log.info(dict(payload=payload, **metadata))
            return messaging.NotificationResult.HANDLED

    def warn(self, ctxt, publisher_id, event_type, payload, metadata):
        log.info('WARN')

    def error(self, ctxt, publisher_id, event_type, payload, metadata):
        log.info('ERROR')

if __name__ == '__main__':
    eventlet.monkey_patch()

    logging.basicConfig()
    log = logging.getLogger()
    log.setLevel(logging.INFO)

    cfg.CONF(sys.argv[1:])
    log.info('Configuring connection')
    transport = messaging.get_notification_transport(cfg.CONF)

    targets = [
        messaging.Target(topic='monitor'),
    ]
    endpoints = [NotificationHandler()]

    server = messaging.get_notification_listener(transport, targets, endpoints, allow_requeue=True, executor='eventlet')
    log.info('Starting up server')
    server.start()
    log.info('Waiting for something')
    server.wait()
