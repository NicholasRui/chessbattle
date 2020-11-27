import time
import chess
import copy
import numpy as np
from func_timeout import func_timeout, FunctionTimedOut

class SampleStockfish:
    """
    Stockfish player class.
    """
    def __init__(self, side, board, max_time_per_move, time_control):
        """
        Initialize player class to implement Stockfish.

        side: str
          Either 'white' or 'black' for the side that the player is expected to play

        board: Board (default: chess.Board())
          Initial board configuration (the default is just the normal board).

        max_time_per_move: float (default: None)
          Max. thinking time (in sec) to be passed to the players.
        
        time_control: 2-tuple of floats (default: None)
          The time control, formatted as (x, y) where the time control is x minutes
          with a y second increment. This argument is distinct from max_time_per_move.
        """
        self.name = 'Stockfish'
        
        self.side = side
        self.board = board
        self.max_time_per_move = max_time_per_move
        self.time_control = time_control
        
        # Manage time control
        if self.time_control is not None and self.max_time_per_move is not None:
            self.time_left = np.min([60 * self.time_control[0], self.max_time_per_move])
        elif self.time_control is not None:
            self.time_left = 60 * self.time_control[0]
        elif self.max_time_per_move is not None:
            self.time_left = self.max_time_per_move
        else:
            self.time_left = None
        
        # Start Stockfish
        from stockfish import Stockfish
        self.stockfish = Stockfish('./stockfish-11-win/Windows/stockfish_20011801_x64_modern.exe')
    
    def make_move(self):
        """
        Method to make a move. Returns the move in UCI.
        """
        self.stockfish.set_fen_position(self.board.fen())
        if self.time_left is not None:
            move = self.stockfish.get_best_move_time(0.8 * self.time_left * 1000)
        else:
            # If no time controls, make this 30 s
            move = self.stockfish.get_best_move_time(30 * 1000)
        
        self.board.push(chess.Move.from_uci(move))
        
        return move
    
    def receive_move(self, move, time_left=None):
        """
        Method to update board with move from the other side.
        
        move: str
          Move that opponent made
        
        time_left: float (default: None)
          Time remaining, if None, there is no global time control
        """
        self.board.push(chess.Move.from_uci(move))
        self.time_left = time_left
        
        return
    
    def request_draw(self):
        """
        Method to request a draw. Return True if want to request a draw, False if not.
        """
        return False
    
    def respond_draw(self):
        """
        Method to respond to a draw request. Return True if accept draw, False if not.
        """
        return False
    
    def receive_trash_talk(self, trash_talk):
        """
        Method to receive trash talk.
        """
        return
    
    def solicit_trash_talk(self):
        """
        Method to solicit trash talk. Return a string to solicit trash talk. If no trash
        talk, return none.
        """
        return None

class SampleMrBean:
    """
    Mr. Bean player class.
    """
    def __init__(self, side, board, max_time_per_move, time_control):
        """
        Initialize player class to implement an idiot bot which plays random moves.

        side: str
          Either 'white' or 'black' for the side that the player is expected to play

        board: Board (default: chess.Board())
          Initial board configuration (the default is just the normal board).

        max_time_per_move: float (default: None)
          Max. thinking time (in sec) to be passed to the players.
        
        time_control: 2-tuple of floats (default: None)
          The time control, formatted as (x, y) where the time control is x minutes
          with a y second increment. This argument is distinct from max_time_per_move.
        """
        self.name = 'Mr. Bean'
        
        self.side = side
        self.board = board
        self.max_time_per_move = max_time_per_move
        self.time_control = time_control
            
    def make_move(self):
        """
        Method to make a move. Returns the move in UCI.
        """
        possible_moves = list(self.board.legal_moves)
        move = np.random.choice(possible_moves).uci()
        
        self.board.push(chess.Move.from_uci(move))
        
        return move
    
    def receive_move(self, move, time_left=None):
        """
        Method to update board with move from the other side.
        
        move: str
          Move that opponent made
        
        time_left: float (default: None)
          Time remaining, if None, there is no global time control
        """
        self.board.push(chess.Move.from_uci(move))
        
        return
    
    def request_draw(self):
        """
        Method to request a draw. Return True if want to request a draw, False if not.
        """
        return False
    
    def respond_draw(self):
        """
        Method to respond to a draw request. Return True if accept draw, False if not.
        """
        return False

    def receive_trash_talk(self, trash_talk):
        """
        Method to receive trash talk.
        """
        return

    def solicit_trash_talk(self):
        """
        Method to solicit trash talk. Return a string to solicit trash talk. If no trash
        talk, return none.
        """
        return None

class SampleHuman:
    """
    Human player class. Accepts user input for the moves.
    """
    def __init__(self, side, board, max_time_per_move, time_control):
        """
        Initialize player class to implement Stockfish.

        side: str
          Either 'white' or 'black' for the side that the player is expected to play

        board: Board (default: chess.Board())
          Initial board configuration (the default is just the normal board).

        max_time_per_move: float (default: None)
          Max. thinking time (in sec) to be passed to the players.
        
        time_control: 2-tuple of floats (default: None)
          The time control, formatted as (x, y) where the time control is x minutes
          with a y second increment. This argument is distinct from max_time_per_move.
        """
        self.name = 'Human'
        
        self.side = side
        self.board = board
        self.max_time_per_move = max_time_per_move
        self.time_control = time_control
        
        # Manage time control
        if self.time_control is not None and self.max_time_per_move is not None:
            self.time_left = np.min([60 * self.time_control[0], self.max_time_per_move])
        elif self.time_control is not None:
            self.time_left = 60 * self.time_control[0]
        elif self.max_time_per_move is not None:
            self.time_left = self.max_time_per_move
        else:
            self.time_left = None
    
    def make_move(self):
        """
        Method to make a move. Returns the move in UCI.
        """
        print(f'{self.side} to move...')
        print('\n')
        print(self.board)
        print('\n')
        
        if self.time_left is not None:
            print(f'  Time left: {self.time_left}')
        
        print('  What is your move?')
        move = input('   > ')
        
        try:
            self.board.push(chess.Move.from_uci(move))
        except:
            pass
        
        return move
    
    def receive_move(self, move, time_left=None):
        """
        Method to update board with move from the other side.
        
        move: str
          Move that opponent made
        
        time_left: float (default: None)
          Time remaining, if None, there is no global time control
        """
        self.board.push(chess.Move.from_uci(move))
        self.time_left = time_left
        
        return
    
    def request_draw(self):
        """
        Method to request a draw. Return True if want to request a draw, False if not.
        """
        draw_str = input('  Type "y" to request a draw. Type anything else to pass. ')
        if draw_str == 'y':
            draw_bool = True
        else:
            draw_bool = False
        
        return draw_bool
    
    def respond_draw(self):
        """
        Method to respond to a draw request. Return True if accept draw, False if not.
        """
        print('  Opponent offers a draw. Type "y" to accept. Type anything else to pass. ')
        draw_str = input('   > ')
        if draw_str == 'y':
            draw_bool = True
        else:
            draw_bool = False
        
        return draw_bool
    
    def receive_trash_talk(self, trash_talk):
        """
        Method to receive trash talk.
        """
        return
    
    def solicit_trash_talk(self):
        """
        Method to solicit trash talk. Return a string to solicit trash talk. If no trash
        talk, return none.
        """
        print('  Any trash talk? ')
        trash_talk = input('   > ')
        
        if len(trash_talk) > 0:
            return trash_talk
        else:
            return None

class CompetitorExamplePlayer:
    """
    Example player class template. This is not a functional class.
    """
    def __init__(self, side, board, max_time_per_move, time_control):
        """
        Initialize player class to implement an idiot bot which plays random moves.

        side: str
          Either 'white' or 'black' for the side that the player is expected to play

        board: Board (default: chess.Board())
          Initial board configuration (the default is just the normal board).

        max_time_per_move: float (default: None)
          Max. thinking time (in sec) to be passed to the players.
        
        time_control: 2-tuple of floats (default: None)
          The time control, formatted as (x, y) where the time control is x minutes
          with a y second increment. This argument is distinct from max_time_per_move.
        """
        self.name = 'Name'
        
        self.side = side
        self.board = board
        self.max_time_per_move = max_time_per_move
        self.time_control = time_control
            
    def make_move(self):
        """
        Method to make a move. Returns the move in UCI.
        """
        
        return move
    
    def receive_move(self, move, time_left=None):
        """
        Method to update board with move from the other side.
        
        move: str
          Move that opponent made
        
        time_left: float (default: None)
          Time remaining, if None, there is no time control
        """
        self.board.push(chess.Move.from_uci(move))
        
        return
    
    def request_draw(self):
        """
        Method to request a draw. Return True if want to request a draw, False if not.
        """
        return False
    
    def respond_draw(self):
        """
        Method to respond to a draw request. Return True if accept draw, False if not.
        """
        return False

    def receive_trash_talk(self, trash_talk):
        """
        Method to receive trash talk.
        """
        return

    def solicit_trash_talk(self):
        """
        Method to solicit trash talk. Return a string to solicit trash talk. If no trash
        talk, return none.
        """
        return None
