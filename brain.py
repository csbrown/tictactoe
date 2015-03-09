from pybrain.structure import TanhLayer, FeedForwardNetwork, LinearLayer, FullConnection
from pybrain.datasets import SupervisedDataSet
from pybrain.supervised.trainers import BackpropTrainer
import random
from pybrain.tools.customxml.networkwriter import NetworkWriter
from pybrain.tools.customxml.networkreader import NetworkReader

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
        self.trainer_settings = { "learningrate" : 0.01,
                                  "momentum" : 0.99
                                }
        self.records = {"win" : 0, "lose" : 0, "tie" : 0}
    
    def create_input_layer(self):
        '''This defines the input layer of a backgammon game'''
        spots = 9
        return LinearLayer(spots)

    def create_output_layer(self):
        '''This defines the output layer of the game'''
        spots = 9
        return LinearLayer(spots)

    def create_hidden_layers(self):
        layers = []
        numlayers = random.randint(4,8)
        for layer in range(numlayers):
            layers.append(TanhLayer(random.randint(9,15)))
        return layers

    def add_layers(self, inp, outp, hiddens):
        self.net.addOutputModule(outp)
        self.net.addInputModule(inp)
        for layer in hiddens:
            self.net.addModule(layer)

    def add_connections(self, inp, outp, hiddens):
        self.net.addConnection(FullConnection(inp, hiddens[0]))
        for i in range(len(hiddens)-1):
            self.net.addConnection(FullConnection(hiddens[i], hiddens[i+1]))
        self.net.addConnection(FullConnection(hiddens[-1], outp))

    def train_outcome(self, playlist, player, correct_output_chooser):
        data = SupervisedDataSet(9, 9)
        for play in playlist:
            if play.player == player:
                correct_output = correct_output_chooser(play.board, play.position, play.player)
                data.addSample(tuple(play.board.board), tuple(correct_output)) 
        trainer = BackpropTrainer(self.net, data, **self.trainer_settings)
        trainer.train()
        
    def win_output_chooser(self, board, position, player):
        correct_output = [0] * 9
        correct_output[position] = 1
        return tuple(correct_output)

    def lose_output_chooser(self, board, position, player):
        correct_output = [0] * 9
        possible_output = [pos for pos in range(0,9) if board.is_legal(pos)]
        correct_output[random.choice(possible_output)] = 1
        return tuple(correct_output)
        
    def train(self, playlist, outcome, player):
        # We won
        if outcome == 1 and player == 1:
            self.train_outcome(playlist, player, self.win_output_chooser)
            self.records["win"] += 1
            
        # We lost
        elif outcome == -1 and player == 1:
            self.train_outcome(playlist, player, self.lose_output_chooser)
            self.records["lose"] += 1

        # We tied
        else:
            self.train_outcome(playlist, player, self.lose_output_chooser)
            self.records["tie"] += 1

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

