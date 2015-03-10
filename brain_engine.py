import Pyro4
import brain
import ai

def playerto(interface_name):
    nameserver = Pyro4.locateNS()
    uri = nameserver.lookup(interface_name)
    return Pyro4.Proxy(uri)          # return a Pyro proxy to the brain object

def playerfrom(player, interface_name):
    daemon = Pyro4.Daemon()
    ns = Pyro4.locateNS()
    uri = daemon.register(player)
    ns.register(interface_name, uri)
    
    daemon.requestLoop()

if __name__=="__main__":
    player = ai.TTTNNAI(filename = "brain.xml")
    playerfrom(player, "tictactoebrain")
    
