import numpy as np
import time
import pdb

# ==============================================================================
# CONSTANTS
# ==============================================================================
ReferenceRank = np.array([[ii for jj in range(8)] for ii in range(8)])
ReferenceFile = np.array([[jj for jj in range(8)] for ii in range(8)])

def algebraic(position):
    """ Converts algebraic notation to grid position. """
    assert type(position) == str
    assert len(position) == 2
    
    return (8 - int(position[1]), {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}[position[0]])

class Board:
    """
    Board object stores chess board together with useful methods and turn
    parameters.
    
    == Parameters ==
    grid, array object (default: None):
      Board grid before move was played
      If None, initialize default board
    
    to_move, str (default: 'white'):
      Player to move, 'white' if white and 'black' if black
    
    check, bool (default: False):
      True if in check, False otherwise
      
    kingside_castled, bool (default: False):
      True if the player to move is unable to castle kingside
      
    queenside_castled, bool (default: False):
      True if the player to move is unable to castle queenside
      
    en_passant, tuple (default: None):
      If int, allow en passants on the file described
    
    == Attributes ==
    
    grid, np.ndarray:
      8x8 array describing the board
      
    == Methods ==
    
    legal_moves, list:
      Lists all legal moves as tuples (initial position, final position, *)
    """
    def __init__(self, grid=None, to_move='white', en_passant=None, kingside_castled=False, queenside_castled=False):        
        if grid is None:
            # Initialize a new board
            self.grid = np.array([['bR', 'bN', 'bB', 'bK', 'bQ', 'bB', 'bN', 'bR'],
                                  ['bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP'],
                                  ['  ', '  ', '  ', '  ', '  ', '  ', '  ', '  '],
                                  ['  ', '  ', '  ', '  ', '  ', '  ', '  ', '  '],
                                  ['  ', '  ', '  ', '  ', '  ', '  ', '  ', '  '],
                                  ['  ', '  ', '  ', '  ', '  ', '  ', '  ', '  '],
                                  ['wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP'],
                                  ['wR', 'wN', 'wB', 'wK', 'wQ', 'wB', 'wN', 'wR']])
        else:
            self.grid = grid
        
        self.to_move = to_move
        self.check = False
        self.kingside_castled = kingside_castled
        self.queenside_castled = queenside_castled
        self.en_passant = en_passant
    
    def make_move(self, move):
        """
        Return modified board.
        """
        grid = np.copy(self.grid)
        
        # Play the move provided it is a legal move and return the modified grid.
        if move in self.legal_moves():
            piece = grid[move[0]]
            grid[move[0]] = '  '
            grid[move[1]] = piece
            
            if len(move) == 3:
                changes = move[2]
                for ii in range(len(changes)):
                    change = changes[ii]
                    
                    grid[change[0]] = change[1]
    
            return grid
        else:
            return None
    
    def legal_moves(self):
        """
        Returns a list of legal moves, in the following format.
        
        (initial position, final position, [list of other environmental changes])
        """
        moves = []
            
        # Write down all moves, noting that you are not allowed to do anything
        # which puts your king into check
        if self.to_move == 'white':
            pref = 'w'
            epref = 'b'
            start_rank = 6
            promote_rank = 1
            forward = -1
        elif self.to_move == 'black':
            pref = 'b'
            epref = 'w'
            start_rank = 1
            promote_rank = 6
            forward = 1
        
        # Pawns
        ranks, files = np.where(self.grid == pref + 'P')
        
        pawn_moves = []
        for ii in range(len(ranks)):                    
            # Check if anything is in front of the pawn, allow move if not
            if self.grid[(ranks[ii] + forward, files[ii])] == '  ':
                if ranks[ii] == promote_rank:
                    pawn_moves.append( ((ranks[ii], files[ii]), (ranks[ii] + forward, files[ii]),
                                        [((promote_rank + forward, files[ii]), pref + 'N')]))
                    pawn_moves.append( ((ranks[ii], files[ii]), (ranks[ii] + forward, files[ii]),
                                        [((promote_rank + forward, files[ii]), pref + 'B')]))
                    pawn_moves.append( ((ranks[ii], files[ii]), (ranks[ii] + forward, files[ii]),
                                        [((promote_rank + forward, files[ii]), pref + 'R')]))
                    pawn_moves.append( ((ranks[ii], files[ii]), (ranks[ii] + forward, files[ii]),
                                        [((promote_rank + forward, files[ii]), pref + 'Q')]))
                else:
                    pawn_moves.append( ((ranks[ii], files[ii]), (ranks[ii] + forward, files[ii])) )
                
            # If on starting rank, can advance two spaces (provided no obstructions)
            if (ranks[ii] == start_rank) and (self.grid[(start_rank + forward, files[ii])] == '  ') and (self.grid[(start_rank + 2 * forward, files[ii])] == '  '):
                pawn_moves.append( ((ranks[ii], files[ii]), (ranks[ii] + 2 * forward, files[ii])) )
                    
            # Diagonal capture mechanism for pawns
            if files[ii] != 7:
                if self.grid[(ranks[ii] + forward, files[ii] + 1)][0] == epref:
                    if ranks[ii] == promote_rank:
                        pawn_moves.append( ((ranks[ii], files[ii]), (ranks[ii] + forward, files[ii] + 1),
                                            [((promote_rank + forward, files[ii] + 1), pref + 'N')]))
                        pawn_moves.append( ((ranks[ii], files[ii]), (ranks[ii] + forward, files[ii] + 1),
                                            [((promote_rank + forward, files[ii] + 1), pref + 'B')]))
                        pawn_moves.append( ((ranks[ii], files[ii]), (ranks[ii] + forward, files[ii] + 1),
                                            [((promote_rank + forward, files[ii] + 1), pref + 'R')]))
                        pawn_moves.append( ((ranks[ii], files[ii]), (ranks[ii] + forward, files[ii] + 1),
                                            [((promote_rank + forward, files[ii] + 1), pref + 'Q')]))
                    else:
                        pawn_moves.append( ((ranks[ii], files[ii]), (ranks[ii] + forward, files[ii] + 1)) )
                    
            if files[ii] != 0:
                if self.grid[(ranks[ii] + forward, files[ii] - 1)][0] == epref:
                    if ranks[ii] == promote_rank:
                        pawn_moves.append( ((ranks[ii], files[ii]), (ranks[ii] + forward, files[ii] - 1),
                                            [((promote_rank + forward, files[ii] - 1), pref + 'N')]))
                        pawn_moves.append( ((ranks[ii], files[ii]), (ranks[ii] + forward, files[ii] - 1),
                                            [((promote_rank + forward, files[ii] - 1), pref + 'B')]))
                        pawn_moves.append( ((ranks[ii], files[ii]), (ranks[ii] + forward, files[ii] - 1),
                                            [((promote_rank + forward, files[ii] - 1), pref + 'R')]))
                        pawn_moves.append( ((ranks[ii], files[ii]), (ranks[ii] + forward, files[ii] - 1),
                                            [((promote_rank + forward, files[ii] - 1), pref + 'Q')]))
                    else:
                        pawn_moves.append( ((ranks[ii], files[ii]), (ranks[ii] + forward, files[ii] - 1)) )
                
            # En passant
            if (files[ii] != 7) and (ranks[ii] == promote_rank - 2 * forward) and (self.en_passant is not None):
                if files[ii] + 1 == self.en_passant:
                    pawn_moves.append( ((ranks[ii], files[ii]), (ranks[ii] + forward, files[ii] + 1),
                                        [((ranks[ii], files[ii] + 1), '  ')]))
            
            if (files[ii] != 0) and (ranks[ii] == promote_rank - 2 * forward) and (self.en_passant is not None):
                if files[ii] - 1 == self.en_passant:
                    pawn_moves.append( ((ranks[ii], files[ii]), (ranks[ii] + forward, files[ii] - 1),
                                        [((ranks[ii], files[ii] - 1), '  ')]))
            
        moves += pawn_moves
            
        # Knights
        ranks, files = np.where(self.grid == pref + 'N')
            
        knight_moves = []
        
        for ii in range(len(ranks)):
            displacements = [(1,2), (1,-2), (-1, 2), (-1, -2),
                             (2,1), (2,-1), (-2, 1), (-2, -1)]
                
            for jj in range(len(displacements)):
                good_rank = (ranks[ii] + displacements[jj][0]) >= 0 and (ranks[ii] + displacements[jj][0]) <= 7
                good_file = (files[ii] + displacements[jj][1]) >= 0 and (files[ii] + displacements[jj][1]) <= 7
                
                if good_rank and good_file:
                    no_self_capture = self.grid[ranks[ii] + displacements[jj][0], files[ii] + displacements[jj][1]][0] != pref
                    
                    if no_self_capture:
                        knight_moves.append( ((ranks[ii], files[ii]), (ranks[ii] + displacements[jj][0], files[ii] + displacements[jj][1])) )
        
        moves += knight_moves
            
        # Bishops
        ranks, files = np.where(self.grid == pref + 'B')
            
        bishop_moves = []
            
        displacements = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        
        for ii in range(len(ranks)):
            for jj in range(len(displacements)):
                unblocked = True
                newrank = ranks[ii]
                newfile = files[ii]
                    
                while unblocked:
                    newrank += displacements[jj][0]
                    newfile += displacements[jj][1]
                        
                    good_rank = (newrank >= 0) and (newrank <= 7)
                    good_file = (newfile >= 0) and (newfile <= 7)
                        
                    if good_rank and good_file:
                        if self.grid[(newrank, newfile)] == '  ':
                            bishop_moves.append( ((ranks[ii], files[ii]), (newrank, newfile)) )
                        elif self.grid[(newrank, newfile)][0] == epref:
                            unblocked = False
                            bishop_moves.append( ((ranks[ii], files[ii]), (newrank, newfile)) )
                        elif self.grid[(newrank, newfile)][0] == pref:
                            unblocked = False
                    else:
                        unblocked = False
            
        moves += bishop_moves
            
        # Rooks
        ranks, files = np.where(self.grid == pref + 'R')
            
        rook_moves = []
        
        displacements = [(1, 0), (0, 1), (-1, 0), (0, -1)]
            
        for ii in range(len(ranks)):
            for jj in range(len(displacements)):
                unblocked = True
                newrank = ranks[ii]
                newfile = files[ii]
                    
                while unblocked:
                    newrank += displacements[jj][0]
                    newfile += displacements[jj][1]
                        
                    good_rank = (newrank >= 0) and (newrank <= 7)
                    good_file = (newfile >= 0) and (newfile <= 7)
                        
                    if good_rank and good_file:
                        if self.grid[(newrank, newfile)] == '  ':
                            rook_moves.append( ((ranks[ii], files[ii]), (newrank, newfile)) )
                        elif self.grid[(newrank, newfile)][0] == epref:
                            unblocked = False
                            rook_moves.append( ((ranks[ii], files[ii]), (newrank, newfile)) )
                        elif self.grid[(newrank, newfile)][0] == pref:
                            unblocked = False
                    else:
                        unblocked = False
            
        moves += rook_moves
        
        # Queens
        ranks, files = np.where(self.grid == pref + 'Q')
            
        queen_moves = []
            
        displacements = [(1, 1), (1, -1), (-1, 1), (-1, -1), (1, 0), (0, 1), (-1, 0), (0, -1)]
            
        for ii in range(len(ranks)):
            for jj in range(len(displacements)):
                unblocked = True
                newrank = ranks[ii]
                newfile = files[ii]
                    
                while unblocked:
                    newrank += displacements[jj][0]
                    newfile += displacements[jj][1]
                        
                    good_rank = (newrank >= 0) and (newrank <= 7)
                    good_file = (newfile >= 0) and (newfile <= 7)
                        
                    if good_rank and good_file:
                        if self.grid[(newrank, newfile)] == '  ':
                            queen_moves.append( ((ranks[ii], files[ii]), (newrank, newfile)) )
                        elif self.grid[(newrank, newfile)][0] == epref:
                            unblocked = False
                            queen_moves.append( ((ranks[ii], files[ii]), (newrank, newfile)) )
                        elif self.grid[(newrank, newfile)][0] == pref:
                            unblocked = False
                    else:
                        unblocked = False
            
        moves += queen_moves

        # Kings
        ranks, files = np.where(self.grid == pref + 'K')
        
        king_moves = []
            
        displacements = [(1, 1), (1, -1), (-1, 1), (-1, -1), (1, 0), (0, 1), (-1, 0), (0, -1)]
            
        for ii in range(len(ranks)):
            for jj in range(len(displacements)):
                newrank = ranks[ii] + displacements[jj][0]
                newfile = files[ii] + displacements[jj][1]
                        
                good_rank = (newrank >= 0) and (newrank <= 7)
                good_file = (newfile >= 0) and (newfile <= 7)
                        
                if good_rank and good_file:
                    if self.grid[(newrank, newfile)] == '  ':
                        king_moves.append( ((ranks[ii], files[ii]), (newrank, newfile)) )
                    elif self.grid[(newrank, newfile)][0] == epref:
                        king_moves.append( ((ranks[ii], files[ii]), (newrank, newfile)) )

        # Castle
        kingside_spots = [(start_rank - forward, 1), (start_rank - forward, 2)]
        queenside_spots = [(start_rank - forward, 4), (start_rank - forward, 5), (start_rank - forward, 6)]
                
        if (self.grid[kingside_spots[0]] == '  ') and (self.grid[kingside_spots[1]] == '  ') and not self.kingside_castled:
            king_moves.append( ((start_rank - forward, 3), (start_rank - forward, 1),
                                [((start_rank - forward, 0), '  '), ((start_rank - forward, 2), pref + 'R')]) )
            
        if (self.grid[queenside_spots[0]] == '  ') and (self.grid[queenside_spots[1]] == '  ') and (self.grid[queenside_spots[2]] == '  ') and not self.queenside_castled:
            king_moves.append( ((start_rank - forward, 3), (start_rank - forward, 5),
                                [((start_rank - forward, 7), '  '), ((start_rank - forward, 4), pref + 'R')]) )
        
        moves += king_moves
        
        
        # PREVENT CASTLING THROUGH CHECK
        
        # REMOVE ANY MOVE WHICH IS NOT ALLOWED BECAUSE OF CHECK
        
        
        return moves
            
    #### WOULD CHECK? METHOD FOR SEEING IF A MOVE WOULD PUT THE KING IN CHECK

class Game:
    """
    store output of game as well as useful info **
    """
    
    def __init__(self, player1=None, player2=None): # fix player functionality
        pass
        # Things to code in
        # * check if 3fold with same player to move
        # * check if 50 moves
        # * check if (can or have) castle
        # * check if en passant
        # * check if mate
        # * check if game cannot be won
        
        # Check how many moves to draw
        return
    
    def play(self):
        # Initialize board
        board = Board(kingside_castled=True, queenside_castled=True)
        print(board.grid)
        
        moveno = 0

        while len(board.legal_moves()) > 0:
            print('')
            print('')
            print('')
            # As a test, randomly play some move
            legal_moves = board.legal_moves()
            move = legal_moves[np.random.randint(len(legal_moves))]
            
            new_grid = board.make_move(move)
            moveno += 1
            
            if moveno > 0:
                time.sleep(0.2)
            
            if board.to_move == 'white':
                board = Board(new_grid, to_move='black', kingside_castled=True, queenside_castled=True)
            elif board.to_move == 'black':
                board = Board(new_grid, to_move='white', kingside_castled=True, queenside_castled=True)
            
            print(board.grid)

        print(moveno)
        return board



