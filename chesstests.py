import time
import chess
import copy
import numpy as np
from func_timeout import func_timeout, FunctionTimedOut

import chessbattle
import chessbots

# Test functions
def test_stockfish_vs_stockfish(max_time_per_move=0.1):
    """
    Stockfish vs. Stockfish
    """
    chessbattle.play_game(chessbots.SampleStockfish, chessbots.SampleStockfish,
                          max_time_per_move_white=max_time_per_move, max_time_per_move_black=max_time_per_move,
                          verbose=True)
    
def test_mrbean_vs_mrbean(seed=0):
    """
    Mr. Bean vs. Mr. Bean
    """
    chessbattle.play_game(chessbots.SampleMrBean, chessbots.SampleMrBean,
                          verbose=True, seed=seed)

def test_mrbean_vs_stockfish(max_time_per_move=0.1, seed=0):
    """
    Mr. Bean vs. Stockfish
    """
    chessbattle.play_game(chessbots.SampleMrBean, chessbots.SampleStockfish,
                          max_time_per_move_white=max_time_per_move, max_time_per_move_black=max_time_per_move,
                          verbose=True, seed=seed)

def test_stockfish_vs_human(max_time_per_move=0.1, seed=0):
    """
    Stockfish vs. Human (time control on white only)
    """
    chessbattle.play_game(chessbots.SampleStockfish, chessbots.SampleHuman,
                          max_time_per_move_white=max_time_per_move, draw_time_black=None, trash_talk_time_black=None)
