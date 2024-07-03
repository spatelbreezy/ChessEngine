import random

piece_scores = {'K': 0, 'Q': 10, 'R': 5, 'B': 3, 'N': 3, 'p': 1}
CHECKMATE = 1000
STALEMATE = 0

#picks and returns a random move
def find_random_move(valid_moves):
    return valid_moves[random.randint(0, len(valid_moves) - 1)] #[a, b] inclusive

#finds the best move based on material alone (greedy algo) (two moves ahead)
def find_best_move(gs, valid_moves): 
    turn_multiplier = 1 if gs.white_to_move else -1 #changes parity based on what side is playing
    opp_minmax_score = CHECKMATE
    best_move = None
    random.shuffle(valid_moves)
    
    for player_move in valid_moves: #finds "best" move
        gs.make_move(player_move) #makes move
        opponents_moves = gs.get_valid_moves()
        opp_max_score = -CHECKMATE
        for opp_move in opponents_moves: #finds opponents max
            gs.make_move(opp_move)
            if gs.checkmate: #checks and calculates score
                score = -turn_multiplier * CHECKMATE
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
