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
        self.move_funcs = {'p': self.get_pawn_moves, 'R': self.get_rook_moves, 'N': self.get_knight_moves,
                            'B': self.get_bishop_moves, 'Q': self.get_queen_moves, 'K': self.get_king_moves}

        self.white_to_move = True
        self.move_log = []

    #Takes a Move object and executes it (no castling, pawn promo, or en-passant)
    def make_move(self, move):
        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.move_log.append(move) #allows undo function
        self.white_to_move = not self.white_to_move #flips to other players move

    #Undos the last move
    def undo_move(self):
        if len(self.move_log) != 0: 
            move = self.move_log.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.captured
            self.white_to_move = not self.white_to_move #switches turn back

    # All moves considering checks
    def get_valid_moves(self):
        return self.get_all_possible() #temporary

    # All moves not considering checks
    def get_all_possible(self):
        moves = []
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                turn = self.board[row][col][0]
                if (turn == 'w' and self.white_to_move) or (turn == 'b' and not self.white_to_move):
                    piece = self.board[row][col][1]
                    self.move_funcs[piece](row, col, moves) #calls appropriate move function based on piece
        return moves
        
    #Get all the pawn moves for the pawn location at (r,c) and adds to list of valid moves
    def get_pawn_moves(self, r, c, moves):
        if self.white_to_move:
            if self.board[r-1][c] == "--": #1 square pawn advance
                moves.append(Move((r,c), (r-1, c), self.board))
                if r==6 and self.board[r-2][c] == "--": #2 square pawn advance
                    moves.append(Move((r,c), (r-2, c), self.board))

            if c-1 >= 0: #captures to left
                if self.board[r-1][c-1][0] == 'b': #possible enemy piece to capture
                    moves.append(Move((r,c), (r-1,c-1), self.board))
            if c+1 <= 7: #captures to right
                if self.board[r+1][c+1][0] == 'b':
                    moves.append(Move((r,c), (r-1,c+1), self.board))

        else: #black pawn moves
            if self.board[r+1][c] == "--":
                moves.append(Move((r,c), (r+1, c), self.board))
                if r==1 and self.board[r+2][c] == "--":
                    moves.append(Move((r,c), (r+2,c), self.board))

            #captures
            if c-1 >= 0:
                if self.board[r+1][c-1][0] == 'w':
                    moves.append(Move((r,c), (r+1, c-1), self.board))
            if c+1 <= 7:
                if self.board[r+1][c+1][0] == 'w':
                    moves.append(Move((r,c), (r+1, c+1), self.board))
        #add pawn promos later:(((
        
    #Get all the rook moves for the rook at location (r,c) and adds to the list of valid moves
    def get_rook_moves(self, r, c, moves): 
        directions = ((-1,0), (0, -1), (1,0), (0,1)) #up down left right
        enemy = 'b' if self.white_to_move else 'w'
        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8: #in bounds
                    end_piece = self.board[end_row][end_col]
                    if end_piece == '--':
                        moves.append(Move((r,c), (end_row, end_col), self.board))
                    elif end_piece[0] == enemy:
                        moves.append(Move((r,c), (end_row, end_col), self.board))
                        break
                    else: #friendly fire xD
                        break
                else: #invalid spot
                    break
      
    #Get all the knight moves for the rook at location (r,c) and adds to the list of valid moves
    def get_knight_moves(self, r, c, moves): 
        directions =  ((-2,-1), (-2,1), (-1,-2), (-1,2), (1,-2), (1,2), (2,-1), (2,1)) #all the ways knight can move!
        ally = "w" if self.white_to_move else "b"
        for move in directions:
            end_row = r + move[0]
            end_col = c + move[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally: #if the piece is an enemy
                    moves.append(Move(r,c), (end_row, end_col), self.board)

    
    #Get all the bishop moves for the rook at location (r,c) and adds to the list of valid moves
    def get_bishop_moves(self, r, c, moves): 
        directions = ((-1,-1), (-1, 1), (1, -1), (1, 1)) #diagonals
        enemy = "b" if self.white_to_move else "w"
        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8: #on board?
                    end_piece = self.board[end_row][end_col]
                    if end_piece == '--': #empty space?
                        moves.append(Move((r,c), (end_row, end_col), self.board))
                    elif end_piece[0] == enemy: #enemy piece?
                        moves.append(Move((r,c), (end_row, end_col), self.board))
                        break
                    else:
                        break
                else: #not on board :(
                    break
        pass   
    
    #Get all the queen moves for the rook at location (r,c) and adds to the list of valid moves
    def get_queen_moves(self, r, c, moves):
        self.get_rook_moves(r, c, moves)
        self.get_bishop_moves(r, c, moves)
   
    
    #Get all the king moves for the rook at location (r,c) and adds to the list of valid moves
    def get_king_moves(self, r, c, moves):
        directions = ((-1,-1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
        ally = "w" if self.white_to_move else "b"
        for i in range(8):
            end_row = r + directions[i][0]
            end_col = c + directions[i][1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally:
                    moves.append(Move((r, c), (end_row, end_col), self.board)) 
        pass             




class Move():
    #rank and file converters (back and forth)
    rank_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {v: k for k, v in rank_to_rows.items()}

    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def __init__(self, start_sq, end_sq, board):
        self.start_row, self.start_col = start_sq[0], start_sq[1]
        self.end_row, self.end_col = end_sq[0], end_sq[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.captured = board[self.end_row][self.end_col]
        self.move_ID = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col * 1 #ID for equals method
    

    #Overriding the equals method
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.move_ID == other.move_ID
        return False


    def get_chess_notation(self):
        return self.get_rank_file(self.start_row, self.start_col) + " -> " + self.get_rank_file(self.end_row, self.end_col)


    def get_rank_file(self, r, c):
        return self.cols_to_files[c] + self.rows_to_ranks[r]