import random

piece_scores = {'K': 0, 'Q': 10, 'R': 5, 'B': 3, 'N': 3, 'p': 1}

#better ways to do this, but sufficient
knight_scores = [   [1, 1, 1, 1, 1, 1, 1, 1],
                    [1, 2, 2, 2, 2, 2, 2, 1],
                    [1, 2, 3, 3, 3, 3, 2, 1],
                    [1, 2, 3, 4, 4, 3, 2, 1],
                    [1, 2, 3, 4, 4, 3, 2, 1],
                    [1, 2, 3, 3, 3, 3, 2, 1],
                    [1, 2, 2, 2, 2, 2, 2, 1],
                    [1, 1, 1, 1, 1, 1, 1, 1]
                ]

bishop_score = [    [4, 3, 2, 1, 1, 2, 3, 4],
                    [3, 4, 3, 2, 2, 3, 4, 3],
                    [2, 3, 4, 3, 3, 4, 3, 2],
                    [1, 2, 3, 4, 4, 3, 2, 1],
                    [1, 2, 3, 4, 4, 3, 2, 1],
                    [2, 3, 4, 3, 3, 4, 3, 2],
                    [3, 4, 3, 2, 2, 3, 4, 3],
                    [4, 3, 2, 1, 1, 2, 3, 4]
               ]

queen_scores = [    [1, 1, 1, 3, 1, 1, 1, 1],
                    [1, 2, 3, 3, 3, 1, 1, 1],
                    [1, 4, 3, 3, 3, 4, 2, 1],
                    [1, 2, 3, 3, 3, 2, 2, 1],
                    [1, 2, 3, 3, 3, 2, 2, 1],
                    [1, 4, 3, 3, 3, 4, 2, 1],
                    [1, 2, 3, 3, 3, 1, 1, 1],
                    [1, 1, 1, 3, 1, 1, 1, 1]
               ]

rook_scores = [     [4, 3, 4, 4, 4, 4, 3, 4],
                    [4, 4, 4, 4, 4, 4, 4, 4],
                    [1, 1, 2, 3, 3, 2, 1, 1],
                    [1, 2, 3, 4, 4, 3, 2, 1],
                    [1, 2, 3, 4, 4, 3, 2, 1],
                    [1, 1, 2, 3, 3, 2, 1, 1],
                    [4, 4, 4, 4, 4, 4, 4, 4],
                    [4, 3, 4, 4, 4, 4, 3, 4]
              ]

whitepawn_scores = [    [8, 8, 8, 8, 8, 8, 8, 8],
                        [8, 8, 8, 8, 8, 8, 8, 8],
                        [5, 6, 6, 7, 7, 6, 6, 5],
                        [2, 3, 3, 5, 5, 3, 3, 2],
                        [1, 2, 3, 4, 4, 3, 2, 1],
                        [1, 1, 2, 3, 3, 2, 1, 1],
                        [1, 1, 1, 0, 0, 1, 1, 1],
                        [0, 0, 0, 0, 0, 0, 0, 0]
                   ]

blackpawn_scores = [    [0, 0, 0, 0, 0, 0, 0, 0],
                        [1, 1, 1, 0, 0, 1, 1, 1],
                        [1, 1, 2, 3, 3, 2, 1, 1],
                        [1, 2, 3, 4, 4, 3, 2, 1],
                        [2, 3, 3, 5, 5, 3, 3, 2],
                        [5, 6, 6, 7, 7, 6, 6, 5],
                        [8, 8, 8, 8, 8, 8, 8, 8],
                        [8, 8, 8, 8, 8, 8, 8, 8]
                   ]

piece_position_scores = {'N': knight_scores, 'Q': queen_scores, 'B': bishop_score, 'R': rook_scores, 
                        'bp': blackpawn_scores, 'wp': whitepawn_scores}
CHECKMATE = 1000
STALEMATE = 0
DEPTH = 4 #bigger will be laggier because of AI smart move picker algorithm

#picks and returns a random move
def find_random_move(valid_moves):
    return valid_moves[random.randint(0, len(valid_moves) - 1)] #[a, b] inclusive

#finds the best move based on material alone (greedy minmax-ish algo) (two moves ahead)
def find_best_move(gs, valid_moves): 
    turn_multiplier = 1 if gs.white_to_move else -1 #changes parity based on what side is playing
    opp_minmax_score = CHECKMATE
    best_move = None
    random.shuffle(valid_moves)
    
    for player_move in valid_moves: #finds "best" move
        gs.make_move(player_move) #makes move
        opponents_moves = gs.get_valid_moves()
        if gs.stalemate:
            opp_max_score = STALEMATE
        elif gs.checkmate:
            opp_max_score = -CHECKMATE
        else:
            opp_max_score = -CHECKMATE
            for opp_move in opponents_moves: #finds opponents max
                gs.make_move(opp_move)
                gs.get_valid_moves()
                if gs.checkmate: #checks and calculates score
                    score = CHECKMATE
                elif gs.stalemate:
                    score = STALEMATE
                else:
                    score = -turn_multiplier * score_material(gs.board)
                if score > opp_max_score:
                    opp_max_score = score
                gs.undo_move()

        if opp_max_score < opp_minmax_score: #minimization part of algo
            opp_minmax_score = opp_max_score
            best_move = player_move

        gs.undo_move() #undos move and goes to next move

    return best_move

#Helper method to make first recurisve call to MinMax algorithm
def find_best_negamax_move(gs, valid_moves):
    global next_move
    next_move = None
    random.shuffle(valid_moves)
    find_move_negaMax(gs, valid_moves, DEPTH, -CHECKMATE, CHECKMATE, 1 if gs.white_to_move else -1)
    return next_move

#recursive MinMax algorithm
def find_move_minmax(gs, valid_moves, depth, is_white_move):
    global next_move
    if depth == 0:
        return score_material(gs.board)

    if is_white_move: #maximize
        max_score = -CHECKMATE
        for move in valid_moves:
            gs.make_move(move)
            next_moves = gs.get_valid_moves()
            score = find_move_minmax(gs, next_moves, depth - 1, False)
            if score > max_score:
                max_score = score
                if depth == DEPTH:
                    next_move = move
            gs.undo_move()
        return max_score
    else: #minimize
        min_score = CHECKMATE
        for move in valid_moves:
            gs.make_move(move)
            next_moves = gs.get_valid_moves()
            score = find_move_minmax(gs, next_moves, depth - 1, True)
            if score < min_score:
                min_score = score
                if depth == DEPTH:
                    next_move = move
            gs.undo_move()
        return min_score

#NegaMax algorithm with alpha beta pruning to find best move
# THIS IS THE BEST ALGORITHM 
def find_move_negaMax(gs, valid_moves, depth, alpha, beta, turn_multiplier):
    global next_move
    if depth == 0:
        return turn_multiplier * score_board(gs)

    #move ordering - evalute the best ones first
    max_score = -CHECKMATE
    for move in valid_moves:
        gs.make_move(move)
        next_moves = gs.get_valid_moves()
        score = -find_move_negaMax(gs, next_moves, depth - 1, -beta, -alpha, -turn_multiplier)
        if score > max_score:
            max_score = score
            if depth == DEPTH:
                next_move = move
        gs.undo_move()
        if max_score > alpha: #pruning
            alpha = max_score
        if alpha >= beta:
            break #no need to continue in this move brnach
             
    return max_score

#Scores entire board
#Positve == good for white
#negative == good for black
def score_board(gs):
    if gs.checkmate:
        if gs.white_to_move:
            return -CHECKMATE #black wins
        else:
            return CHECKMATE #white wins
    elif gs.stalemate:
        return STALEMATE


    score = 0
    #zero sum game
    for row in range(len(gs.board)):
        for col in range(len(gs.board[row])):
            square = gs.board[row][col]
            if square != '--':
                #score positionally
                pos_score = 0
                if square[1] != 'K':
                    if square[1] == 'p': #pawns only
                        pos_score = piece_position_scores[square][row][col]
                    else:
                        pos_score = piece_position_scores[square[1]][row][col]

                if square[0] == 'w':
                    score += piece_scores[square[1]] + pos_score * 0.2
                elif square[0] == 'b':
                    score -= piece_scores[square[1]] + pos_score * 0.2


    return score

#Score board based on material
def score_material(board):
    score = 0

    #zero sum game
    for row in board:
        for square in row:
            if square[0] == 'w':
                score += piece_scores[square[1]]
            elif square[0] == 'b':
                score -= piece_scores[square[1]]
    
    return score
