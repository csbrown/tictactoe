import cPickle
import brain
from pybrain.tools.customxml.networkreader import NetworkReader
import numpy as np
import sys
import random

class TTTPlayer(object):
    def __init__(self):
        self.record = {"win" : 0, "lose" : 0, "tie" : 0}

    def get_play(self, board, which_player):
        pass

    def inform_illegal_play(self, board, which_player, position):
        raise Exception(self.__class__.__name__ + " made an illegal play at position {} on board: \n {}".format(position, str(board)))

    def inform_winner(self, which_player, winner, playlist):
        if which_player == winner:
            self.record["win"] += 1
        elif winner == 0:
            self.record["tie"] += 1
        else:
            self.record["lose"] += 1

    def free_spaces(self, board):
        '''which spaces are free'''
        return [i for i in range(0,9) if board.is_legal(i)]

class TTTPerfectAI(TTTPlayer):

    def recurse_ahead(self, board, which_player):
        '''Given a board node, search all child nodes and return (the best space to play, who the expected winner is under optimal play)'''

        # If there is a winner, return that
        winner = board.is_winner()
        free = self.free_spaces(board)
        if winner:
            return (None, winner)
        # If the game has tied, return that 
        elif len(free) == 0:
            return (None, 0)

        # if a space wins, return that space, else, recurse
        children = []
        for space in free:
            copy = board.copy()
            copy.update_board(space, which_player)
            children.append((space, self.recurse_ahead(copy, which_player*(-1))[1]))

        # Pick the best move from possible moves
        best = children[0]
        for child in children[1:]:
            # If we can win, do it
            if child[1] == which_player:
                return child
            # if we can't win, take a tie
            elif child[1] == 0:
                best = child

        return best

    def get_play(self, board, which_player):
        # First play
        if len(self.free_spaces(board)) == 9:
            return 4
        # Second play
        if len(self.free_spaces(board)) == 8:
            # Take middle if possible
            if board.is_legal(4):
                return 4
            # If not, the corners are free, take a corner
            return 0
        # Third play
        if len(self.free_spaces(board)) <= 7:
            # 7! is small, so we can search the state space to the end.  The opponent could not have forced a win yet, so we force a win or a tie
            return self.recurse_ahead(board, which_player)[0]    
            
        

class TTTMediumAI(TTTPlayer):

    def look_ahead(self, board, which_player):
        '''If a player can win on the next move, return that position, elif the opponent can win on the next move, go there'''
        for player in [which_player, -1*which_player]:
            for i in range(0, 9):
                copy = board.copy()
                if copy.is_legal(i):
                    copy.update_board(i, player)
                    if copy.is_winner():
                        return i
        return None

    def get_play(self, board, which_player):
        '''This method looks two moves ahead for wins'''
        position = self.look_ahead(board, which_player)
        #If somebody can win on the next move, go there
        if position:
            return position
        #If nobody can win on the next move, for every possible move, look ahead as opponent, and take their best move
        for i in [i for i in range(0,9) if board.is_legal(i)]:
            copy = board.copy()
            copy.update_board(i, which_player)
            position = self.look_ahead(copy, -1*which_player)
            if position:
                return position

        # Otherwise, choose a space in this order:
        spaces = [0,2,6,8, #corners
                  4,       #middle
                  7,5,3,1] #sides
        space_goodness_weights = np.array([0.2, 0.2, 0.2, 0.2, 
                                           0.1, 
                                           0.025, 0.025, 0.025, 0.025])
        space_legality = np.array([1 if board.is_legal(i) else 0 for i in spaces])
        space_legal_weights = space_goodness_weights * space_legality
        space_weights = space_legal_weights / sum(space_legal_weights)
        position = int(np.random.choice(spaces, p = space_weights))
        return position

        

class TTTEasyAI(TTTPlayer):

    def get_play(self, board, which_player):
        # If you can win, do it, then, if the opponent can win, stop him
        for player in [which_player, -1*which_player]:
            for i in range(0, 9):
                copy = board.copy()
                if copy.is_legal(i):
                    copy.update_board(i, player)
                    if copy.is_winner():
                        return i

        # Otherwise, choose a space in this order:
        space_goodness = [0,2,6,8, #corners
                          4,       #middle
                          7,5,3,1] #sides
        for i in space_goodness:
            copy = board.copy()
            if copy.is_legal(i):
                return i


class TTTRandomAI(TTTPlayer):
    def get_play(self, board, which_player):
        return random.choice(self.free_spaces(board))

 
class TTTNNAI(TTTPlayer):
    def __init__(self, filename = None):
        TTTPlayer.__init__(self)
        self.brain = brain.TTTBrain()
        if not filename:
            self.brain.fresh()
        else:
            self.brain.load(filename)
        
    def get_play(self, board, which_player):
        # Consult the brain
        found_position = False
        possibilities = self.brain.net.activate(tuple(board.board))
        return max(range(0,9), key = lambda i: possibilities[i] + board.is_legal(i)*10000000000)

    def inform_winner(self, which_player, winner, playlist):
        TTTPlayer.inform_winner(self, which_player, winner, playlist)
        self.brain.train(playlist, winner)


class TTTHuman(TTTPlayer):
    def get_play(self, board, which_player):
        print board
        legal = False
        while not legal:
            position = int(raw_input("move?"))
            legal = board.is_legal(position)
        return position

    def inform_winner(self, which_player, winner, playlist):
        TTTPlayer.inform_winner(self, which_player, winner, playlist)
        if which_player == winner:
            print "You win!"
        elif winner == 0:
            print "Tie!"
        else:
            print "You lose!"

        


