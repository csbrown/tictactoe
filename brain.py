from pybrain.structure import TanhLayer, FeedForwardNetwork, LinearLayer, FullConnection, SoftmaxLayer
from pybrain.datasets import SupervisedDataSet
from pybrain.supervised.trainers import BackpropTrainer
import random
from pybrain.tools.customxml.networkwriter import NetworkWriter
from pybrain.tools.customxml.networkreader import NetworkReader
import tttengine

class TTTBrain(object):
    '''
    This class defines a brain for a tic tac toe game
    inputs: 1 for x on a spot,
            -1 for o on a spot
            spots numbered from 1 to 9
    outputs: probabilities to play on each of the various spots
    NB: Can the network represent illegal moves somehow?
    '''
    def __init__(self):
        self.trainer_settings = { "learningrate" : 0.2,
                                  "momentum" : 0.9
                                }
    
    def create_input_layer(self):
        '''This defines the input layer of a backgammon game'''
        spots = 9
        return LinearLayer(spots)

    def create_output_layer(self):
        '''This defines the output layer of the game'''
        spots = 9
        return SoftmaxLayer(spots)

    def create_hidden_layers(self):
        layers = []
        numlayers = 3
        for layer in range(numlayers):
            #(5 - abs(layer - 5))
            layers.append(TanhLayer(9))
        return layers

    def add_layers(self, inp, outp, hiddens):
        self.net.addOutputModule(outp)
        self.net.addInputModule(inp)
        for layer in hiddens:
            self.net.addModule(layer)

    def add_complete_connections(self, inp, outp, hiddens):
        all_layers = [inp] + hiddens + [outp]
        for i in range(len(all_layers) - 1):
            self.net.addConnection(FullConnection(all_layers[i], all_layers[i + 1]))

    def add_connections(self, inp, outp, hiddens):
        self.net.addConnection(FullConnection(inp, hiddens[0]))
        for i in range(len(hiddens)-1):
            self.net.addConnection(FullConnection(hiddens[i], hiddens[i+1]))
        self.net.addConnection(FullConnection(hiddens[-1], outp))
        
    def win_output_chooser(self, position):
        correct_output = [0] * 9
        correct_output[position] = 1
        return tuple(correct_output)
        
    def train(self, playlist, winner):
        data = SupervisedDataSet(9, 9)
        for play in playlist:
            if play.player == winner or winner == 0:
                correct_output = self.win_output_chooser(play.position)
                data.addSample(tuple(play.board.board), tuple(correct_output)) 
        trainer = BackpropTrainer(self.net, data, **self.trainer_settings)
        trainer.train()

    def train_illegal(self, board, position):
        player = random.choice([1, -1])
        playlist = [tttengine.TTTPlay(board, position, player)]
        self.train(playlist, player*(-1), player)

    def dump(self, filename):
        '''Save this network to file'''
        NetworkWriter.writeToFile(self.net, filename)

    def load(self, filename):
        '''Load and existing network'''
        self.net = NetworkReader.readFrom(filename)

    def fresh(self):
        '''Create a fresh network'''
        self.net = FeedForwardNetwork()

        inp = self.create_input_layer()
        outp = self.create_output_layer()
        hiddens = self.create_hidden_layers()
        self.add_layers(inp, outp, hiddens)
        self.add_connections(inp, outp, hiddens)
        self.net.sortModules()
        
        
        
if __name__ == "__main__":
    brain = TTTBrain()
    brain.fresh()
    print brain.net.activate((1,1,0,-1,-1,0,1,-1,0))
    brain.dump("brain.xml")

