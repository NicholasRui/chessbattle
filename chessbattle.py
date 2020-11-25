import time
import chess
import copy
import numpy as np
from func_timeout import func_timeout, FunctionTimedOut

import pdb



# to do:
# - implement draw
# - implement trash talk
# - write an output file
# - visualization




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
        self.side = side
        self.board = board
        self.max_time_per_move = max_time_per_move
        self.time_control = time_control
        
        from stockfish import Stockfish
        self.stockfish = Stockfish('./stockfish-11-win/Windows/stockfish_20011801_x64_modern.exe')
    
    def make_move(self):
        """
        Method to make a move. Returns the move in UCI.
        """
        self.stockfish.set_fen_position(self.board.fen())
        
        if self.max_time_per_move is not None:
            move = self.stockfish.get_best_move_time(0.8 * self.max_time_per_move * 1000)
        else:
            move = self.stockfish.get_best_move_time(1e3)
        
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
    
    def solicit_trash_talk(self):
        """
        Method to solicit trash talk. Return a string to solicit trash talk. If no trash
        talk, return none.
        """
        return None




    



def play_game(PlayerWhite, PlayerBlack, max_time_per_move=None, time_control=None, seed=0, board=chess.Board(fen=chess.STARTING_FEN)):
    """
    Initializes game.
    
    ----------
    Parameters
    ----------
    PlayerWhite: Class
      Player class corresponding to the white pieces.
    
    PlayerBlack: Class
      Player class corresponding to the black pieces.
    
    max_time_per_move: float (default: None)
      Max. thinking time (in sec) to be passed to the players.
    
    time_control: 2-tuple of floats (default: None)
      The time control, formatted as (x, y) where the time control is x minutes
      with a y second increment. This argument is distinct from max_time_per_move.
    
    seed: int (default: 0)
      Random seed used to initialize state.
    
    board: Board (default: chess.Board())
      Initial board configuration (the default is just the normal board).
    """
    np.random.seed(seed)
    board = copy.deepcopy(board)
    
    white = PlayerWhite(side='white',
                        board=copy.copy(board),
                        max_time_per_move=max_time_per_move,
                        time_control=time_control)
    black = PlayerBlack(side='black',
                        board=copy.copy(board),
                        max_time_per_move=max_time_per_move,
                        time_control=time_control)
    
    # Sort the players based on which one is going first in this board configuration
    if board.turn:
        players = [white, black]
        player_names = ['white', 'black']
        player_bools = [True, False]
    else:
        players = [black, white]
        player_names = ['black', 'white']
        player_bools = [False, True]
    
    if time_control is not None:
        total_time0 = 60 * time_control[0]
        total_time1 = 60 * time_control[0]
        increment = time_control[1]
        player_names = ['white', 'black']
    
    player0_times = []
    player1_times = []
    
    first_turn = True
    
    while True:
        ########################################################################
        # PLAYER 0
        ########################################################################
        
        # Player 0 time control
        if time_control is not None and max_time_per_move is not None:
            timeout0 = np.max([total_time0, max_time_per_move])
        elif time_control is not None:
            timeout0 = total_time0
        elif max_time_per_move is not None:
            timeout0 = max_time_per_move
        else:
            timeout0 = None
        
        # Construct player 0 move
        if first_turn:
            def turn0():
                move0 = players[0].make_move()
                
                return move0
            
            first_turn = False
        else:
            if time_control is not None:
                def turn0():
                    players[0].receive_move(move1, time_left=total_time0)
                    move0 = players[0].make_move()
                    
                    return move0
                    
            else:
                def turn0():
                    players[0].receive_move(move1, time_left=None)
                    move0 = players[0].make_move()
                    
                    return move0
        
        # Attempt to perform player 0 move
        try:
            start = time.time()
            move0 = func_timeout(timeout=timeout0, func=turn0)
            time0 = time.time() - start
            
            if timeout0 is not None: # if python delay finishes up but external code runs over, correct time
                time0 = np.min([time0, timeout0])
        except FunctionTimedOut: # runs out of time
            if board.has_insufficient_material(player_bools[1]):
                game_result = f'Draw:timeout with insufficient material'
            else:
                game_result = f'Win {player_names[1]}:timeout'
            break
        except: # another error is thrown
            game_result = f'Win {player_names[1]}:runtime error'
            break
        
        # Update player 0 time control
        if time_control is not None:
            total_time0 -= time0
            total_time0 += increment
        
        # Attempt to push move
        if not board.is_legal(chess.Move.from_uci(move0)): # illegal move
            game_result = f'Win {player_names[1]}:illegal move'
            break
        try:
            board.push(chess.Move.from_uci(move0))
        except: # invalid move
            game_result = f'Win {player_names[1]}:invalid move'
            break
        
        # Check if game ends naturally
        if board.is_game_over():
            if board.is_checkmate():
                game_result = f'Win {player_names[0]}:checkmate'
            if board.is_stalemate():
                game_result = f'Draw:stalemate'
            if board.is_insufficient_material():
                game_result = f'Draw:insufficient material'
            if board.can_claim_threefold_repetition():
                game_result = f'Draw:threefold repetition'
            if board.can_claim_fifty_moves():
                game_result = f'Draw:fifty-move rule'
            
            break
        
        print(f'white: {time0} s')
        print(board)
        print('\n')
        
        ########################################################################
        # PLAYER 1
        ########################################################################
        
        # Player 1 time control
        if time_control is not None and max_time_per_move is not None:
            timeout1 = np.max([total_time0, max_time_per_move])
        elif time_control is not None:
            timeout1 = total_time1
        elif max_time_per_move is not None:
            timeout1 = max_time_per_move
        else:
            timeout1 = None
        
        # Construct player 1 move
        if time_control is not None:
            def turn1():
                players[1].receive_move(move0, time_left=total_time1)
                move1 = players[1].make_move()
                
                return move1
                
        else:
            def turn1():
                players[1].receive_move(move0, time_left=None)
                move1 = players[1].make_move()
                
                return move1
        
        # Attempt to perform player 1 move
        try:
            start = time.time()
            move1 = func_timeout(timeout=timeout1, func=turn1)
            time1 = time.time() - start
            
            if timeout1 is not None: # if python delay finishes up but external code runs over, correct time
                time1 = np.min([time1, timeout1])
        except FunctionTimedOut: # runs out of time
            if board.has_insufficient_material(player_bools[0]):
                game_result = f'Draw:timeout with insufficient material'
            else:
                game_result = f'Win {player_names[0]}:timeout'
            break
        except: # another error is thrown
            game_result = f'Win {player_names[0]}:runtime error'
            break
        
        # Update player 1 time control
        if time_control is not None:
            total_time1 -= time1
            total_time1 += increment
        
        # Attempt to push move
        if not board.is_legal(chess.Move.from_uci(move1)): # illegal move
            game_result = f'Win {player_names[0]}:illegal move'
            break
        try:
            board.push(chess.Move.from_uci(move1))
        except: # invalid move
            game_result = f'Win {player_names[0]}:invalid move'
            break
        
        # Check if game ends naturally
        if board.is_game_over():
            if board.is_checkmate():
                game_result = f'Win {player_names[1]}:checkmate'
            if board.is_stalemate():
                game_result = f'Draw:stalemate'
            if board.is_insufficient_material():
                game_result = f'Draw:insufficient material'
            if board.can_claim_threefold_repetition():
                game_result = f'Draw:threefold repetition'
            if board.can_claim_fifty_moves():
                game_result = f'Draw:fifty-move rule'
            
            break
        
        print(f'black: {time1} s')
        print(board)
        print('\n')
    
    print(board)
    print('\n')
    print(game_result)    
    
    
    
    
    
    
    # do timing
    # draw
    
    # write out:
    # - response times
    # - moves
    # outcome
    # metadata about the game
    ...







# Tests
def test_stockfish_vs_stockfish(seed=0):
    play_game(SampleStockfish, SampleStockfish, seed=seed)

def test_stockfish_vs_stockfish_time_control_1(seed=0):
    play_game(SampleStockfish, SampleStockfish, time_control=(3,2), seed=seed)

def test_stockfish_vs_stockfish_time_control_2(t=0.3, seed=0):
    play_game(SampleStockfish, SampleStockfish, max_time_per_move=t, seed=seed)
    
def test_mrbean_vs_mrbean(seed=0):
    play_game(SampleMrBean, SampleMrBean, seed=seed)

def test_mrbean_vs_stockfish(seed=0):
    play_game(SampleMrBean, SampleStockfish, seed=seed)
















