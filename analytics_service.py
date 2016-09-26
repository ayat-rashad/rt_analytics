from werkzeug.wrappers import Response
from analytics_manager import AnalyticsManager, setup_log
import redis
from config import *

from weakref import WeakKeyDictionary
from datetime import datetime
import json
import zlib

import tornado.ioloop
import tornado.web
from tornado import wsgi


_log = setup_log('service')
client = redis.Redis(REDIS_HOST, REDIS_PORT, unix_socket_path='/tmp/redis.sock')
manager = AnalyticsManager(client)



class MainHandler(tornado.web.RequestHandler):
    def prepare(self):
        if self.request.headers["Content-Type"].startswith("application/json"):
            try:
                self.json_args = json.loads(self.request.body)
            except Exception as e:
                _log.error('%s: %s' %(type(e), e))
                self.json_args = None
        else:
            self.json_args = None

    #def on_finish(self):
    #    self.set_header("Content-Type", "application/json")


class EventHandler(MainHandler):
    def post(self):
        if self.json_args == None:
            _log.error('error: could not find request data, make sure it is json.')
            self.set_status(500)
            self.write({'error': 'could not find request data, make sure it is json.'})
            return

        event = self.json_args
        code, data = manager.store_event(event)

        if code != 0:
            self.set_status(500)
        else:
            self.set_status(200)

        self.write(data)


class CampHandler(MainHandler):
    def post(self):
        if self.json_args == None:
            self.set_status(500)
            _log.error('error: could not find request data, make sure it is json.')
            self.write({'error': 'could not find request data, make sure it is json.'})
            return

        event = self.json_args
        code, data = manager.get_camp_data(event)

        if code != 0:
            self.set_status(500)
            self.write(data)
            return

        response_data = zlib.compress(json.dumps(data))
        self.set_status(200)
        self.set_header("Content-Type", "json")
        self.set_header("Content-Encoding", "gzip")
        self.write(response_data)


# Application and its wsgi interface
application = tornado.web.Application([
    (r"/event", EventHandler),
    (r"/camp", CampHandler)
])
wsgi_app = wsgi.WSGIAdapter(application)
