# Engine stores all information about the current state of the game. 
# Allows the main driver to interact with the current state of the game. 
# Also determines valid moves. 

class GameState():
    def __init__(self): 
        #board is an 8x8 2d list. Each element has 2 characters
        #The first character represents color. 'b' ==  black, 'w' == white
        #The second character represents the type of piece. 'K', 'Q', 'N, 'R', 'B', 'p' 
        # '--' signfies empty position with no piece.
        self.board = [ 
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
        ]

        self.white_to_move = True
        self.move_log = []
