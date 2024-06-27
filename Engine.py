# Engine stores all information about the current state of the game. 
# Allows the main driver to interact with the current state of the game. 
# Also determines valid moves. 

class GameState:
    def __init__(self): 
        #board is a 8x8 2d list. Each element has 2 characters
        #The first character represents color. 'b' ==  black, 'w' == white
        #The second character represents the type of piece. 'K', 'Q', 'N, 'R', 'B', 'p' 
        # '--' signifies empty position with no piece.
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

        self.checkmate = False
        self.stalemate = False
        self.enPassant = () #where it CAN happen (possible sqr)
        #castling rights
        self.wK_castle = True
        self.wQ_castle = True
        self.bK_castle = True
        self.bQ_castle = True
        self.castle_log = [CastleRights(self.wK_castle, self.bK_castle, self.wQ_castle, self.bQ_castle)]

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

        #if pawn moves twice, next move can capture enpassant
        if move.piece_moved[1] == 'p' and abs(move.start_row - move.end_row) == 2:
            self.enPassant = ((move.end_row + move.start_row) // 2, move.end_col)
        else:
            self.enPassant = ()
        
        #if enPassant move. must update board to capture pawn
        if move.enPassant:
            self.board[move.start_row][move.end_col] = '--'
        #if pawn promo change piece
        if move.pawn_promo:
            promoted = input("Promote to Q, R, B, or N:") #added to ui
            self.board[move.end_row][move.end_col] = move.piece_moved[0] + promoted

        #update castling
        self.update_castle(move)
        self.castle_log.append(CastleRights(self.wK_castle, self.bK_castle, self.wQ_castle, self.bQ_castle))

        if move.castle:
            if move.end_col - move.start_col == 2:
                self.board[move.end_row][move.end_col - 1] = self.board[move.end_row][move.end_col + 1]
                self.board[move.end_row][move.end_col + 1] = '--'
            else: #queen side
                self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 2]
                self.board[move.end_row][move.end_col - 2] = '--'


 
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
            
            if move.enPassant:
                self.board[move.end_row][move.end_col] = '--'
                self.board[move.start_row][move.end_col] = move.captured
                self.enPassant = (move.end_row, move.end_col)
            
            if move.piece_moved[1] == 'p' and abs(move.start_row - move.end_row) == 2:
                self.enPassant = ()

            self.castle_log.pop()
            castle_rights = self.castle_log[-1]
            self.wK_castle = castle_rights.wks
            self.bK_castle = castle_rights.bks
            self.wQ_castle = castle_rights.wqs
            self.bQ_castle = castle_rights.bqs

    #All moves considering checks
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
                valid_squares = []
                if piece_checking[1] == 'N':
                    valid_squares = [(check_row, check_col)]
                else:
                    for i in range(1, 8):
                        sqr = (king_row + check[2]*i, king_col + check[3]*i) 
                        valid_squares.append(sqr)
                        if sqr[0] == check_row and valid_squares[1] == check_col:
                            break
                #reverse traversal and get rid of any moves that don't block check or move king
                for i in range(len(moves)-1, -1, -1): 
                    if moves[i].piece_moved[1] != "K": #does not move king
                        if (moves[i].end_row, moves[i].end_col) not in valid_squares:
                            moves.remove(moves[i])
            else: #double check
                self.get_king_moves(king_row, king_col, moves)
        else: #not in check so all moves are valid
            moves = self.get_all_possible()                 
        
        if len(moves) == 0:
            if self.in_check:
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False

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
                    if end_piece[0] == ally and end_piece[1] != 'K':
                        if possible_pin == ():
                            possible_pin = (end_row, end_col, d[0], d[1])
                        else:
                            break
                    elif end_piece[0] == enemy:
                        type = end_piece[1]
                        #5 diff possibilities
                        #1) orthogonally away from king and piece is rook
                        #2) diagonally away from king and piece is bishop
                        #3) 1 sqr away diagonally from king and piece is a pawn
                        #4) any direction and piece is a queen
                        #5) any direction 1 away and piece is a king
                        if (0 <= j <= 3 and type == 'R') or \
                            (4 <= j <= 7 and type == 'B') or \
                                (i == 1 and type == 'p' and
                                 ((enemy == 'w' and 6 <= j <= 7) or (enemy == 'b' and 4 <= j <= 5))) or \
                                    (type == 'Q') or (i == 1 and type == 'K'):
                            if possible_pin == ():
                                in_check = True
                                checks.append((end_row, end_col, d[0], d[1]))
                                break
                            else: #piece blocking == pin!
                                pins.append(possible_pin)
                                break
                        else:  #enemy not applying check
                            break
                else:
                    break #off board !
        #check for knight checks
        knight_directions = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for m in knight_directions:
            end_row, end_col = start_row + m[0], start_col + m[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] == enemy and end_piece[1] == 'N': #enemy knight attacking king
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
        is_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                is_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.white_to_move:
            move_amt, start_row, back_row, enemy = -1, 6, 0, 'b'
        else:
            move_amt, start_row, back_row, enemy = 1, 1, 7, 'w'
        promo = False

        if self.board[r + move_amt][c] == '--':
            if not is_pinned or pin_direction == (move_amt, 0):
                if r + move_amt == back_row:
                    promo = True
                moves.append(Move((r, c), (r + move_amt, c), self.board, pawn_promo=promo))
                if r == start_row and self.board[r + 2*move_amt][c] == '--':
                    moves.append(Move((r, c), (r + 2*move_amt, c), self.board))

        if c - 1 >= 0: #capture to left
            if not is_pinned or pin_direction == (move_amt, -1):
                if self.board[r + move_amt][c - 1][0] == enemy:
                    if r + move_amt == back_row:
                        promo = True
                    moves.append(Move((r, c), (r + move_amt, c - 1), self.board, pawn_promo=promo))
                if (r + move_amt, c - 1) == self.enPassant:
                    moves.append(Move((r, c), (r + move_amt, c - 1), self.board, enPassant=True))
        if c + 1 <= 7: #capture to right
            if not is_pinned or pin_direction == (move_amt, 1):
                if self.board[r + move_amt][c + 1][0] == enemy:
                    if r + move_amt == back_row:
                        promo = True
                    moves.append(Move((r, c), (r + move_amt, c + 1), self.board, pawn_promo=promo))
                if (r + move_amt, c + 1) == self.enPassant:
                    moves.append(Move((r, c), (r + move_amt, c + 1), self.board, enPassant=True))            

        
    #Get all the rook moves for the rook at location (r,c) and adds to the list of valid moves
    def get_rook_moves(self, r, c, moves): 
        is_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                is_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != 'Q':
                    self.pins.remove(self.pins[i])
                break
        
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1)) #up down left right
        enemy = 'b' if self.white_to_move else 'w'
        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8: #in bounds
                    if not is_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]):
                        end_piece = self.board[end_row][end_col]
                        if end_piece == '--':
                            moves.append(Move((r, c), (end_row, end_col), self.board))
                        elif end_piece[0] == enemy:
                            moves.append(Move((r, c), (end_row, end_col), self.board))
                            break
                        else: #friendly fire xD
                            break
                else: #invalid spot
                    break
      
    #Get all the knight moves for the rook at location (r,c) and adds to the list of valid moves
    def get_knight_moves(self, r, c, moves): 
        is_pinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                is_pinned = True
                self.pins.remove(self.pins[i])
                break
        directions =  ((-2,-1), (-2,1), (-1,-2), (-1,2), (1,-2), (1,2), (2,-1), (2,1)) #all the ways knight can move!
        ally = "w" if self.white_to_move else "b"
        for move in directions:
            end_row = r + move[0]
            end_col = c + move[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                if not is_pinned:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] != ally: #if the piece is an enemy
                        moves.append(Move((r,c), (end_row, end_col), self.board))

    
    #Get all the bishop moves for the rook at location (r,c) and adds to the list of valid moves
    def get_bishop_moves(self, r, c, moves): 
        is_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                is_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1)) #diagonals
        enemy = "b" if self.white_to_move else "w"
        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8: #on board?
                    if not is_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]):
                        end_piece = self.board[end_row][end_col]
                        if end_piece == '--': #empty space?
                            moves.append(Move((r, c), (end_row, end_col), self.board))
                        elif end_piece[0] == enemy: #enemy piece?
                            moves.append(Move((r, c), (end_row, end_col), self.board))
                            break
                        else:
                            break
                else: #not on board :(
                    break
    
    #Get all the queen moves for the rook at location (r,c) and adds to the list of valid moves
    def get_queen_moves(self, r, c, moves):
        self.get_rook_moves(r, c, moves)
        self.get_bishop_moves(r, c, moves)
   
    
    #Get all the king moves for the rook at location (r,c) and adds to the list of valid moves
    def get_king_moves(self, r, c, moves):
        row_moves = (-1, -1, -1, 0, 0, 1, 1, 1)
        col_moves = (-1, 0, 1, -1, 1, -1, 0, 1)
        ally = "w" if self.white_to_move else "b"
        for i in range(8):
            end_row = r + row_moves[i]
            end_col = c + col_moves[i]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally:
                    if ally == 'w':
                        self.wK_location = (end_row, end_col)
                    else:
                        self.bK_location = (end_row, end_col)
                    in_check, pins, checks = self.check_pins_and_checks()
                    if not in_check:
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                    
                    if ally == 'w':
                        self.wK_location = (r, c)
                    else:
                        self.bK_location = (r, c)

    def update_castle(self, move):
        if move.piece_moved == 'wK':
            self.wK_castle = False
            self.wQ_castle = False
        elif move.piece_moved == 'bK':
            self.bK_castle = False
            self.bQ_castle = False
        elif move.piece_moved == 'wR':
            if move.start_row == 7:
                if move.start_col == 7:
                    self.wK_castle = False
                elif move.start_col == 0:
                    self.wQ_castle = False
        elif move.piece_moved == 'bR':
            if move.start_row == 0:
                if move.start_col == 7:
                    self.bK_castle = False
                elif move.start_col == 0:
                    self.bQ_castle = False

class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move():
    #rank and file converters (back and forth)
    rank_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {v: k for k, v in rank_to_rows.items()}

    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def __init__(self, start_sq, end_sq, board, enPassant=False, pawn_promo=False, castle=False):
        self.start_row, self.start_col = start_sq[0], start_sq[1]
        self.end_row, self.end_col = end_sq[0], end_sq[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.captured = board[self.end_row][self.end_col]
        self.enPassant = enPassant
        self.pawn_promo = pawn_promo
        self.castle = castle
        if enPassant:
            self.captured = 'bp' if self.piece_moved == 'wp' else 'wp'
        self.move_ID = (self.start_row * 1000 + self.start_col * 100
                        + self.end_row * 10 + self.end_col * 1) #ID for equals method
        
    

    #Overriding the equals method
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.move_ID == other.move_ID
        return False


    def get_chess_notation(self):
        return (self.get_rank_file(self.start_row, self.start_col) + " -> "
                + self.get_rank_file(self.end_row, self.end_col))


    def get_rank_file(self, r, c):
        return self.cols_to_files[c] + self.rows_to_ranks[r]