from txthings import coap, resource
from json import dumps
from twisted.internet import defer, reactor

node = None

class ActorsResource(resource.CoAPResource):

    def __init__(self):
        resource.CoAPResource.__init__(self)

    def render_GET(self, request):
        global node
        actors = node.am.list_actors()
        response = coap.Message(code = coap.CONTENT, payload = dumps(actors))
        return defer.succeed(response)

class CoAPServer:

    def __init__(self, the_node):
        global node
        node = the_node
        self.root = resource.CoAPResource()
        self.root.putChild('actors', ActorsResource())

    def start(self):
        reactor.listenUDP(coap.COAP_PORT, coap.Coap(resource.Endpoint(self.root)))