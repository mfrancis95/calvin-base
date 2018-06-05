from txthings import resource
from txthings.coap import Coap, COAP_PORT, CONTENT, Message
from json import dumps
from calvin.runtime.north.calvinsys import get_calvinsys
from calvin.runtime.north.calvinlib import get_calvinlib
from twisted.internet.defer import succeed
from twisted.internet.reactor import listenUDP

class _ActorsResource(resource.CoAPResource):

    def __init__(self, node):
        resource.CoAPResource.__init__(self)
        self.node = node

    def render_GET(self, request):
        actors = self.node.am.list_actors()
        response = Message(code = CONTENT, payload = dumps(actors))
        return succeed(response)

class _CapabilitiesResource(resource.CoAPResource):

    def __init__(self):
        resource.CoAPResource.__init__(self)

    def render_GET(self, request):
        capabilities = get_calvinsys().list_capabilities() + get_calvinlib().list_capabilities()
        response = Message(code = CONTENT, payload = dumps(capabilities))
        return succeed(response)

class _IdResource(resource.CoAPResource):

    def __init__(self, node):
        resource.CoAPResource.__init__(self)
        self.node = node

    def render_GET(self, request):
        response = Message(code = CONTENT, payload = dumps({'id': self.node.id}))
        return succeed(response)

class CoAPServer:

    def __init__(self, node):
        self.root = resource.CoAPResource()
        self.root.putChild('actors', _ActorsResource(node))
        self.root.putChild('capabilities', _CapabilitiesResource())
        self.root.putChild('id', _IdResource(node))

    def start(self):
        listenUDP(COAP_PORT, Coap(resource.Endpoint(self.root)))