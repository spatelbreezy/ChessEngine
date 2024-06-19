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
        self.wK_location = (7, 4) #white king location
        self.bK_location = (0, 4) #black king location
        self.in_check = False
        self.pins = []
        self.checks = []

    #Takes a Move object and executes it (no castling, pawn promo, or en-passant)
    def make_move(self, move):
        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.move_log.append(move) #allows undo function
        self.white_to_move = not self.white_to_move #flips to other players move
        if move.piece_moved == "wK":
            self.wK_location = (move.end_row, move.end_col)
        elif move.piece_moved == "bK":
            self.bK_location = (move.end_row, move.end_col)


    #Undos the last move
    def undo_move(self):
        if len(self.move_log) != 0: 
            move = self.move_log.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.captured
            self.white_to_move = not self.white_to_move #switches turn back
            if move.piece_moved == "wK":
                self.wK_location = (move.start_row, move.start_col)
            elif move.piece_moved == "bK":
                self.bK_location = (move.start_row, move.start_col)
            

    # All moves considering checks
    def get_valid_moves(self):
        moves = []
        self.in_check, self.pins, self.checks = self.check_pins_and_checks()
        if self.white_to_move:
            king_row, king_col = self.wK_location[0], self.wK_location[1]
        else:
            king_row, king_col = self.bK_location[0], self.bK_location[1]
        
        if self.in_check:
            if len(self.checks) == 1: #only 1 possible check, block check or move king!
                moves = self.get_all_possible() #all possible moves
                check = self.checks[0] #check info
                check_row, check_col = check[0], check[1]
                piece_checking = self.board[check_row][check_col]
                valid_sqrs = []
                if piece_checking[1] == 'N':
                    valid_sqrs = [(check_row, check_col)]
                else:
                    for i in range(1, 8):
                        sqr = (king_row + check[2]*i, king_col + check[3]*i) 
                        valid_sqrs.append(sqr)
                        if sqr[0] == check_row and valid_sqrs[1] == check_col:
                            break
                #reverse traversal and get rid of any moves that dont block check or move king
                for i in range(len(moves)-1, -1, -1): 
                    if moves[i].piece_moved[1] != "K": #does not move king
                        if (moves[i].end_row, moves[i].end_col) not in valid_sqrs:
                            moves.remove(moves[i])
            else: #double check
                self.get_king_moves(king_row, king_col, moves)
        else: #not in check so all moves are valid
            moves = self.get_all_possible()                 
        
        return moves

    def check_pins_and_checks(self):
        pins = []
        checks = []
        in_check = False
        if self.white_to_move:
            enemy = "b"
            ally = "w"
            start_row, start_col = self.wK_location[0], self.wK_location[1]
        else: #black's turn
            enemy = "w"
            ally = "b"
            start_row, start_col = self.bK_location[0], self.bK_location[1]

        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possible_pin = () #resets possible pins
            for i in range(1, 8):
                end_row = start_row + d[0] * i
                end_col = start_col + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8: #on board
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] == ally:
                        if possible_pin == ():
                            possible_pin = (end_row, end_col, d[0], d[1])
                        else:
                            break
                    elif end_piece[0] == enemy:
                        type = end_piece[1]
                        #5 diff possibilites
                        #1) orthogonally away from king and piece is rook
                        #2) diagonally away from king and piece is bishop
                        #3) 1 sqr away diagonally from king and piece is a pawn
                        #4) any direction and piece is a queen
                        #5) any direction 1 away and piece is a king
                        if (0 <= j <= 3 and type == 'R') or \
                            (4 <= j <= 7 and type == 'B') or \
                                (i == 1 and type == 'p' and ((enemy == 'w' and 6 <= j <= 7) or (enemy == 'b' and 4 <= j <= 5))) or \
                                    (type == 'Q') or (i == 1 and type == 'K'):
                            if possible_pin == ():
                                in_check = True
                                checks.append((end_row, end_col, d[0], d[1]))
                                break
                            else:
                                pins.append(possible_pin)
                                break
                        else:   
                            break
        
        knight_directions = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for m in knight_directions:
            end_row, end_col = start_row + m[0], start_col + m[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] == enemy and end_piece[1] == 'N':
                    in_check = True
                    checks.append((end_row, end_col, m[0], m[1]))

        return (in_check, pins, checks)

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
                    moves.append(Move((r,c), (end_row, end_col), self.board))

    
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