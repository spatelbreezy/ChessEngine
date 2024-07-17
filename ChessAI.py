import random

piece_scores = {'K': 0, 'Q': 10, 'R': 5, 'B': 3, 'N': 3, 'p': 1}
CHECKMATE = 1000
STALEMATE = 0
DEPTH = 3

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
    find_move_negaMax(gs, valid_moves, DEPTH, 1 if gs.white_to_move else -1)
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
def find_move_negaMax(gs, valid_moves, depth, turn_multiplier):
    global next_move
    if depth == 0:
        return turn_multiplier * score_board(gs)

    max_score = -CHECKMATE
    for move in valid_moves:
        gs.make_move(move)
        next_moves = gs.get_valid_moves()
        score = -find_move_negaMax(gs, next_moves, depth - 1, -turn_multiplier)
        if score > max_score:
            max_score = score
            if depth == DEPTH:
                next_move = move
        gs.undo_move()
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
    for row in gs.board:
        for square in row:
            if square[0] == 'w':
                score += piece_scores[square[1]]
            elif square[0] == 'b':
                score -= piece_scores[square[1]]
    
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
