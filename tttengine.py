import brain
import easyAI
import time
import sys
from pybrain.tools.customxml.networkwriter import NetworkWriter


class TTTPlay(object):
    def __init__(self, board, position, player):
        self.board = board
        self.position = position
        self.player = player
    def __str__(self):
        return str(self.player) + ":" + str(self.position) + "\n" + str(self.board) 
    __repr__ = __str__

class TTTBoard(object):
    def __init__(self):
        self.board = [0] * 9

    def copy(self):
        board = TTTBoard()
        board.board = [i for i in self.board]
        return board

    def __str__(self):
        board = map(lambda x: "X" if x == 1 else ("O" if x == -1 else " "), self.board)
        hline = "-----\n"
        row = "{}|{}|{}\n"
        return (row+hline+row+hline+row).format(*board)

    def is_full(self):
        for position in self.board:
            if position == 0:
                return False
        return True

    def is_winner(self):
        # Determines if the game is won, and the outcome
        board = self.board

        runs = [board[7]+board[8]+board[6], #bottom
                board[4]+board[5]+board[3], #middle
                board[1]+board[2]+board[0], #top
                board[1]+board[4]+board[7], #middle
                board[2]+board[5]+board[8], #right
                board[3]+board[6]+board[0], #left
                board[0]+board[4]+board[8], #diagonal
                board[2]+board[4]+board[6]] #other diagonal
        if max(runs) == 3:
            return 1
        if min(runs) == -3:
            return -1

    def is_legal(self, position):
        # Determine if a move is legal
        return type(position) is int and 0 <= position < len(self.board) and self.board[position] == 0

    def update_board(self, position, player):
        self.board[position] = player


class TTTGame(object):
    '''This is a class representing the game of tic tac toe'''
    def __init__(self, Xplayer, Oplayer, verbose = False, tbm = 0):
        self.players = [None, Xplayer, Oplayer] # This way player X is 1, and player O is -1
        self.board = TTTBoard()
        self.playlist = [] # keep a playlist of the game

        self.verbose = verbose
        self.tbm = tbm

    def update_board(self, position, player):
        self.playlist.append(TTTPlay(self.board.copy(), position, player))
        self.board.update_board(position, player)
        if self.verbose:
            print self.board
        if self.tbm:
            time.sleep(self.tbm)
        
    def play(self):
        over = False
        current_player = 1
        while not over:
            player_board = self.board.copy() # Get a copy of the board to give to players
            # Get a play from the current player, given the current board state and which player he is
            position = self.players[current_player].get_play(player_board, current_player)
            # Determine if the play is legal
            if self.board.is_legal(position):
                # if the play is legal, play it, check for winner and switch play
                self.update_board(position, current_player)

                winner = self.board.is_winner()
                if winner: 
                    over = True
                elif self.board.is_full():
                    winner = 0
                    over = True
                
                current_player *= -1
            else:
                # if the play isn't legal, inform the player, and try again
                self.players[current_player].inform_illegal_play(player_board, current_player, position)

        for player in [-1,1]:
            self.players[player].inform_winner(player, winner, self.playlist)
            
def record_compare(record1, record2):
    return record1["win"] + record1["tie"] > record2["win"] + record2["tie"]

if __name__ == "__main__":
    MAI = easyAI.TTTMediumAI()
    best_record = {"tie" : 0, "win" : 0, "lose" : 100}
    for i in range(1):

        NNAI = easyAI.TTTNNAI(filename = "best.xml")
        for j in range(1000000):
            if not j % 100000: 
                print "=",
                sys.stdout.flush()
            game = TTTGame(NNAI, MAI, verbose = False, tbm = 0)
            game.play()
        if record_compare(NNAI.brain.records, best_record):
            #NNAI.brain.dump("best.xml")
            best_record = NNAI.brain.records
            print best_record
        #NNAI.brain.dump("brain.xml")
    #NNAI.brain.load("best.xml")
    #NNAI.brain.dump("brain.xml")
