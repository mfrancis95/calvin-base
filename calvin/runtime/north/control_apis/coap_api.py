from txthings import resource
from txthings.coap import Coap, COAP_PORT, CONTENT, Message
from json import dumps
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

class CoAPServer:

    def __init__(self, node):
        self.root = resource.CoAPResource()
        self.root.putChild('actors', _ActorsResource(node))

    def start(self):
        listenUDP(COAP_PORT, Coap(resource.Endpoint(self.root)))