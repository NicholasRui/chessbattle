import time
import chess
import copy
import numpy as np
from func_timeout import func_timeout, FunctionTimedOut

def play_game(PlayerWhite, PlayerBlack, max_time_per_move_white=None, max_time_per_move_black=None,
              time_control_white=None, time_control_black=None, seed=0, board=chess.Board(fen=chess.STARTING_FEN),
              draw_time_white=5, trash_talk_time_white=1, draw_time_black=5, trash_talk_time_black=1, verbose=False, write=None):
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
    
    verbose: bool (default: False)
      If True, print out the board at each step for diagnostic purposes.
    
    write: str (default: None)
      If specified, write the game into a file with the filename specified here.
    """
    np.random.seed(seed)
    board = copy.deepcopy(board)
    init_fen = board.fen()
    
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
        
        if trash_talk is not None:
            try:
                func_timeout(timeout=trash_talk_time1, func=players[1].receive_trash_talk, args=(trash_talk,))
            except FunctionTimedOut:
                move_log += f'{player_names[1]} | trash talk reception timed out\n'
            except:
                move_log += f'{player_names[1]} | trash talk reception threw error\n'
        
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
        
        if verbose:
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
            move_log += f'{player_names[1]} | trash talk solicitation timed out\n'
        except:
            move_log += f'{player_names[1]} | trash talk solicitation threw error\n'
        
        if trash_talk is not None:
            try:
                func_timeout(timeout=trash_talk_time0, func=players[0].receive_trash_talk, args=(trash_talk,))
            except FunctionTimedOut:
                move_log += f'{player_names[0]} | trash talk reception timed out\n'
            except:
                move_log += f'{player_names[0]} | trash talk reception threw error\n'
        
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
        
        if verbose:
            print(f'black: {time1} s')
            print(board)
            print('\n')
    
    if verbose:
        print(board)
        print('\n')
        print(game_result)
        
        print(move_log)
    
    if write is not None:
        text = '--Setup--'
        text += f'fname:{write}\n'
        text += f'white:{white.name}\n'
        text += f'black:{black.name}\n'
        text += f'Init_fen:{init_fen}\n'
        text += '--Time Control--\n'
        
        text += f'max_time_per_move_white:{max_time_per_move_white}\n'
        text += f'max_time_per_move_black:{max_time_per_move_black}\n'
        text += f'time_control_white:{time_control_white}\n'
        text += f'time_control_black:{time_control_black}\n'
        text += f'draw_time_white:{draw_time_white}\n'
        text += f'draw_time_black:{draw_time_black}\n'
        text += f'trash_talk_time_white:{trash_talk_time_white}\n'
        text += f'trash_talk_time_black:{trash_talk_time_black}\n'
        text += '--Game--\n'
        
        text += move_log
        
        f = open(write, 'w')
        f.write(text)
        f.close()
