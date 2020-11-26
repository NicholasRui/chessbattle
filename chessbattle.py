import time
import chess
import copy
import numpy as np
from func_timeout import func_timeout, FunctionTimedOut

import pdb



# to do:
# - write up rules
#    - draw time = 5
#    - trash talk time
#    - set a time control
#    - set a procedure for inquiries, requesting permission to use a package > anon upon request, "sensitive info" is redacted
#    - need to have a name, and need to provide a png personifying your engine - teams of two
#    - explain what all the things do
#    - procedure for crashing
#    - 10 games, if tied, need, continue to play games until someone wins up until 20, and then flip a dice
#    - not allowed to numpy.seed
#    - not allowed to use stockfish evaluation or anything, YOU ARE allowed to use the abilities of 
# - implement ability to receive and respond to trash talk
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

    



def play_game(PlayerWhite, PlayerBlack, max_time_per_move_white=None, max_time_per_move_black=None,
              time_control_white=None, time_control_black=None, seed=0, board=chess.Board(fen=chess.STARTING_FEN),
              draw_time_white=5, trash_talk_time_white=1, draw_time_black=5, trash_talk_time_black=1):
    """
    Initializes game.
    
    ----------
    Parameters
    ----------
    PlayerWhite: Class
      Player class corresponding to the white pieces.
    
    PlayerBlack: Class
      Player class corresponding to the black pieces.
    
    max_time_per_move_white: float (default: None)
      Max. thinking time (in sec) to be passed to white.
    
    max_time_per_move_black: float (default: None)
      Max. thinking time (in sec) to be passed to black.
    
    time_control_white: 2-tuple of floats (default: None)
      The time control for white, formatted as (x, y) where the time control is x
      minutes with a y second increment. This argument is distinct from max_time_per_move_white.
    
    time_control_black: 2-tuple of floats (default: None)
      The time control for black, formatted as (x, y) where the time control is x
      minutes with a y second increment. This argument is distinct from max_time_per_move_black.
    
    seed: int (default: 0)
      Random seed used to initialize state.
    
    board: Board (default: chess.Board())
      Initial board configuration (the default is just the normal board).
    
    draw_time_white: float (default: 5)
      Time in seconds that a player is allowed to take to decide to offer a draw
      or to accept one.

    trash_talk_time_white: float (default: 1)
      Time in seconds that a player is allowed to take to produce trash talk.

    draw_time_black: float (default: 5)
      Time in seconds that a player is allowed to take to decide to offer a draw
      or to accept one.

    trash_talk_time_black: float (default: 1)
      Time in seconds that a player is allowed to take to produce trash talk.
    """
    np.random.seed(seed)
    board = copy.deepcopy(board)
        
    # Sort the players based on which one is going first in this board configuration
    white = PlayerWhite(side='white',
                        board=copy.copy(board),
                        max_time_per_move=max_time_per_move_white,
                        time_control=time_control_white)
    black = PlayerBlack(side='black',
                        board=copy.copy(board),
                        max_time_per_move=max_time_per_move_black,
                        time_control=time_control_black)
    
    if board.turn:
        players = [white, black]
        player_names = ['white', 'black']
        player_bools = [True, False]
        time_control0 = time_control_white
        max_time_per_move0 = max_time_per_move_white
        time_control1 = time_control_black
        max_time_per_move1 = max_time_per_move_black
        draw_time0 = draw_time_white
        draw_time1 = draw_time_black
        trash_talk_time0 = trash_talk_time_white
        trash_talk_time1 = trash_talk_time_black
    else:
        players = [black, white]
        player_names = ['black', 'white']
        player_bools = [False, True]
        time_control0 = time_control_black
        max_time_per_move0 = max_time_per_move_black
        time_control1 = time_control_white
        max_time_per_move1 = max_time_per_move_white
        draw_time0 = draw_time_black
        draw_time1 = draw_time_white
        trash_talk_time0 = trash_talk_time_black
        trash_talk_time1 = trash_talk_time_white
    
    if time_control0 is not None:
        total_time0 = 60 * time_control0[0]
        increment0 = time_control0[1]
    if time_control1 is not None:
        total_time1 = 60 * time_control1[0]
        increment1 = time_control1[1]
    
    # Start game
    player0_times = []
    player1_times = []
    
    first_turn = True
    
    move_log = ''
    
    while True:
        ########################################################################
        # PLAYER 0
        ########################################################################
        
        # Player 0 time control
        if time_control0 is not None and max_time_per_move0 is not None:
            timeout0 = np.max([total_time0, max_time_per_move0])
        elif time_control0 is not None:
            timeout0 = total_time0
        elif max_time_per_move0 is not None:
            timeout0 = max_time_per_move0
        else:
            timeout0 = None
        
        # Construct player 0 move
        if first_turn:
            def turn0():
                move0 = players[0].make_move()
                
                return move0
            
            first_turn = False
        else:
            if timeout0 is not None:
                def turn0():
                    players[0].receive_move(move1, time_left=timeout0)
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
        if time_control0 is not None:
            total_time0 -= time0
            total_time0 += increment0
        
        # Attempt to offer draw
        draw_request = False
        try:
            if func_timeout(timeout=draw_time0, func=players[0].request_draw):
                move_log += f'{player_names[0]} | offers draw\n'
                draw_request = True
        except FunctionTimedOut:
            move_log += f'{player_names[0]} | draw solicitation timed out\n'
        except:
            move_log += f'{player_names[0]} | draw solicitation threw error\n'
        
        if draw_request:
            try:
                if func_timeout(timeout=draw_time1, func=players[1].respond_draw):
                    move_log += f'{player_names[1]} | accepts draw\n'
                    game_result = 'Draw:agreement' 
                    break
                else:
                    move_log += f'{player_names[1]} | declines draw\n'
            except FunctionTimedOut:
                move_log += f'{player_names[1]} | draw response timed out\n'
            except:
                move_log += f'{player_names[1]} | draw response threw error\n'
        
        # Solicit trash talk
        trash_talk = None
        try:
            trash_talk = func_timeout(timeout=trash_talk_time0, func=players[0].solicit_trash_talk)
            if trash_talk is not None:
                if isinstance(trash_talk, str):
                    move_log += f'{player_names[0]} | says:{trash_talk}\n'
                else:
                    move_log += f'{player_names[0]} | trash talk solicitation gave invalid type\n'
        except FunctionTimedOut:
            move_log += f'{player_names[0]} | trash talk solicitation timed out\n'
        except:
            move_log += f'{player_names[0]} | trash talk solicitation threw error\n'
        
        # Log move
        move_log += f'{player_names[0]} t={time0} | move:{move0}\n'
        
        # Attempt to push move
        legality = False
        try:
            legality = board.is_legal(chess.Move.from_uci(move0))
        except: # invalid move
            game_result = f'Win {player_names[1]}:invalid move'
            break
        
        if not board.is_legal(chess.Move.from_uci(move0)): # illegal move
            game_result = f'Win {player_names[1]}:illegal move'
            break
        
        board.push(chess.Move.from_uci(move0))
        
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
        if time_control1 is not None and max_time_per_move1 is not None:
            timeout1 = np.max([total_time0, max_time_per_move1])
        elif time_control1 is not None:
            timeout1 = total_time1
        elif max_time_per_move1 is not None:
            timeout1 = max_time_per_move1
        else:
            timeout1 = None
        
        # Construct player 1 move
        if timeout1 is not None:
            def turn1():
                players[1].receive_move(move0, time_left=timeout1)
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
        if time_control1 is not None:
            total_time1 -= time1
            total_time1 += increment1
        
        # Attempt to offer draw
        draw_request = False
        try:
            if func_timeout(timeout=draw_time1, func=players[1].request_draw):
                move_log += f'{player_names[1]} | offers draw\n'
                draw_request = True
        except FunctionTimedOut:
            move_log += f'{player_names[1]} | draw solicitation timed out\n'
        except Exception as e:
            print(e)
            move_log += f'{player_names[1]} | draw solicitation threw error\n'
        
        if draw_request:
            try:
                if func_timeout(timeout=draw_time0, func=players[0].respond_draw):
                    move_log += f'{player_names[0]} | accepts draw\n'
                    game_result = 'Draw:agreement' 
                    break
                else:
                    move_log += f'{player_names[0]} | declines draw\n'
            except FunctionTimedOut:
                move_log += f'{player_names[0]} | draw response timed out\n'
            except:
                move_log += f'{player_names[0]} | draw response threw error\n'
        
        # Solicit trash talk
        trash_talk = None
        try:
            trash_talk = func_timeout(timeout=trash_talk_time1, func=players[1].solicit_trash_talk)
            if trash_talk is not None:
                if isinstance(trash_talk, str):
                    move_log += f'{player_names[1]} | says:{trash_talk}\n'
                else:
                    move_log += f'{player_names[1]} | trash talk solicitation gave invalid type\n'
        except FunctionTimedOut:
            move_log += f'{player_names[0]} | trash talk solicitation timed out\n'
        except:
            move_log += f'{player_names[0]} | trash talk solicitation threw error\n'
        
        # Log move
        move_log += f'{player_names[1]} t={time1} | move:{move1}\n'
        
        # Attempt to push move
        legality = False
        try:
            legality = board.is_legal(chess.Move.from_uci(move1))
        except: # invalid move
            game_result = f'Win {player_names[0]}:invalid move'
            break
        
        if not board.is_legal(chess.Move.from_uci(move1)): # illegal move
            game_result = f'Win {player_names[0]}:illegal move'
            break
        
        board.push(chess.Move.from_uci(move1))
        
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
    
    print(move_log)
    
    
    
    
    # do timing
    # draw
    
    # write out:
    # metadata about the game
    ...







# Tests
def test_stockfish_vs_stockfish(seed=0):
    play_game(SampleStockfish, SampleStockfish, seed=seed)

def test_stockfish_vs_stockfish_time_control_1(seed=0):
    play_game(SampleStockfish, SampleStockfish, time_control_white=(3,2), seed=seed)

def test_stockfish_vs_stockfish_time_control_2(t=0.3, seed=0):
    play_game(SampleStockfish, SampleStockfish, max_time_per_move_white=t, max_time_per_move_black=t, seed=seed)

def test_stockfish_vs_stockfish_time_control_3(t=0.3, seed=0):
    play_game(SampleStockfish, SampleStockfish, max_time_per_move_white=t, max_time_per_move_black=2*t, seed=seed)
    
def test_mrbean_vs_mrbean(seed=0):
    play_game(SampleMrBean, SampleMrBean, seed=seed)

def test_mrbean_vs_stockfish(seed=0):
    play_game(SampleMrBean, SampleStockfish, seed=seed)

def test_stockfish_vs_human(t=0.3, seed=0):
    play_game(SampleStockfish, SampleHuman, max_time_per_move_white=t, draw_time_black=None, trash_talk_time_black=None)














