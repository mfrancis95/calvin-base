# -*- coding: utf-8 -*-

# Copyright (c) 2018 Ericsson AB
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json

from twisted.internet.defer import succeed
from twisted.internet.reactor import listenUDP
from txthings import resource

from txthings.coap import Message, CONTENT, BAD_REQUEST
from txthings.coap import Coap, COAP_PORT
from txthings.coap import error, requests
from calvin.utilities.calvinlogger import get_logger

from calvin.runtime.north.control_apis import routes
#from control_apis import routes

_log = get_logger(__name__)

_calvincoapcontrol = None

def get_coapcontrol(node=None):
    global _calvincoapcontrol
    if _calvincoapcontrol is None:
        _calvincoapcontrol = CalvinControlCoAP(node)
    return _calvincoapcontrol

class SimpleResource(resource.CoAPResource):
    def __init__(self, control, func, method, path=None):
        resource.CoAPResource.__init__(self)
        self.visible = True
        self.control = control
        self.func = func
        self.path = path
        self.isLeaf = True
        _log.info("Adding method render_{} for handle{}".format(method, func.__name__))
        setattr(self, "render_" + method, self.my_render)

    def my_render(self, request):
        opts = request.postpath
        try:
            node = self.control.node
            response = Message(code=CONTENT, payload=json.dumps(self.func(*opts)))
        except Exception as e:
            _log.error("Failed: {}".format(e))
            response = Message(code=BAD_REQUEST)
        return succeed(response)

class CalvinControlCoAP(object):

    def __init__(self, node):
        self.node = node
        self.root = resource.CoAPResource()
        well_known = resource.CoAPResource()
        self.root.putChild('.well-known', well_known)
        routes.install_coap_handlers(self, self.node.control)

    def add_route(self, method, route, opts, func):
        # route has an "extra" /
        base_route = route[1:]
        path = base_route.split('/', 1)
        resource_obj = SimpleResource(self, func, method)
        _log.info("Adding simple COAP path: {} {}".format(method, base_route))
        self.root.putChild(base_route, resource_obj)

    def start(self):
        listenUDP(COAP_PORT, Coap(resource.Endpoint(self.root)))

    def stop(self):
        pass