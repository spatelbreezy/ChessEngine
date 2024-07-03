# Main driver file. 
# Handles user input and displays the current game state. 
import Engine
import ChessAI
import pygame as p

WIDTH = HEIGHT = 512
DIMENSION = 8 
SQ_SIZE = HEIGHT // DIMENSION #size of each board square
MAX_FPS = 15 
IMAGES: dict[str, str] = {}  

#Initializes a global dictionary of images
def load_images():
    pieces = ['bB', 'bK', 'bN', 'bp', 'bQ', 'bR', 'wB', 'wK', 'wN', 'wp', 'wQ', 'wR']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
    #Access: IMAGES['wK'], etc


#The main driver for our code. 
#Handles user input and updating the graphics
def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    p.display.set_caption("Sahil's Chess Engine")
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = Engine.GameState()
    valid_moves = gs.get_valid_moves()
    move_made = False #flag variable for when move is made
    animate = False #flag variable for when we should animate
    load_images()
    running = True
    selected_sq = () #default is no selected square, stores a tuple (row,col)
    player_clicks = [] #keeps track of clicks, 2 tuples with start(x,y) and end(x,y)
    game_over = False
    player_one = False #If a human is playing white, then this will be true. If an AI is playing, then false
    player_two = False #same as above but for black

    while running:
        is_human_turn = (gs.white_to_move and player_one) or (not gs.white_to_move and player_two)


        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            #mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                if not game_over and is_human_turn:
                    location = p.mouse.get_pos() #x,y location
                    row, col = location[1]//SQ_SIZE, location[0]//SQ_SIZE
                    if selected_sq == (row, col): #selected same square
                        selected_sq = ()
                        player_clicks = []
                    else:
                        selected_sq = (row, col)
                        player_clicks.append(selected_sq)
                    if len(player_clicks) == 2: #after second click
                        move = Engine.Move(player_clicks[0], player_clicks[1], gs.board)
                        print(move.get_chess_notation())
                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]:
                                gs.make_move(valid_moves[i])
                                move_made = True
                                animate = True
                                selected_sq = () 
                                player_clicks = []
                        if not move_made:
                            player_clicks = [selected_sq]
            #key handlers
            elif e.type == p.KEYDOWN:
                if e.key  == p.K_z: #undo when 'z' is pressed
                    gs.undo_move()
                    move_made = True
                    animate = False
                if e.key == p.K_r: #resets board when 'r' is pressed
                    gs = Engine.GameState()
                    valid_moves = gs.get_valid_moves()
                    selected_sq = ()
                    player_clicks = []
                    move_made = False
                    animate = False
        #AI Move finder logic
        if not game_over and not is_human_turn:
            ai_move = ChessAI.find_random_move(valid_moves)
            gs.make_move(ai_move)
            move_made = True
            animate = True
            

        if move_made:
            if animate:
                animate_move(gs.move_log[-1], screen, gs.board, clock)
            valid_moves = gs.get_valid_moves()
            move_made = False
            animate = False

        draw_gamestate(screen, gs, valid_moves, selected_sq)
        if gs.checkmate:
            game_over = True
            if gs.white_to_move:
                draw_text(screen, "Black wins by checkmate!")
            else:
                draw_text(screen, "White wins by checkmate!")
        elif gs.stalemate:
            game_over = True
            draw_text(screen, "Stalemate!")

        clock.tick(MAX_FPS)
        p.display.flip()

#Highlight square selected and moves for piece selected
def highlight_squares(screen, gs, valid_moves, selected_sq):
    if selected_sq != ():
        r, c = selected_sq
        if gs.board[r][c][0] == ('w' if gs.white_to_move else 'b'): #if selected sq is valid piece
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(75) #transparency -> 0 = transparent, 255 = opaque
            s.fill(p.Color('green'))
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))
            #highlight other moves
            s.fill(p.Color('yellow'))
            for move in valid_moves:
                if move.start_row == r and move.start_col == c:
                    screen.blit(s, (SQ_SIZE*move.end_col, SQ_SIZE*move.end_row))

#Draws the given game state 
#Responsible for all graphics witihin a current game state!
def draw_gamestate(screen, gs, valid_moves, selected_sq):
    draw_board(screen) 
    highlight_squares(screen, gs, valid_moves, selected_sq)
    draw_pieces(screen, gs.board) 


#Draws squares on board    
def draw_board(screen):
    global colors
    colors = [p.Color(227,193,111), p.Color(184,139,74)]
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            color = colors[((row + col) % 2)]
            p.draw.rect(screen, color, p.Rect(col*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))

#Draws pieces on top of the board
def draw_pieces(screen, board):
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            piece = board[row][col]
            if piece != "--": #not empty square 
                screen.blit(IMAGES[piece], p.Rect(col*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))

#animating a move
def animate_move(move, screen, board, clock):
    global colors
    deltaR = move.end_row - move.start_row
    deltaC = move.end_col - move.start_col
    frame_per_sq = 10
    frame_count = (abs(deltaR) + abs(deltaC)) * frame_per_sq
    for frame in range(frame_count + 1):
        r, c = (move.start_row + deltaR*frame/frame_count, move.start_col + deltaC*frame/frame_count)
        draw_board(screen)
        draw_pieces(screen, board)
        color = colors[(move.end_row + move.end_col) % 2]
        end_sq = p.Rect(move.end_col*SQ_SIZE, move.end_row*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, end_sq)
        if move.captured != '--':
            screen.blit(IMAGES[move.captured], end_sq)
        screen.blit(IMAGES[move.piece_moved], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)

def draw_text(screen, text):
    font = p.font.SysFont('Helvitca', 48, True, False)
    text_obj = font.render(text, 0, p.Color('Gray'))
    text_loc = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - text_obj.get_width() / 2, HEIGHT/2 - text_obj.get_height() / 2)
    screen.blit(text_obj, text_loc)
    text_obj = font.render(text, 0, p.Color('Black'))
    screen.blit(text_obj, text_loc.move(2, 2))

#if imported, this will still work!
if __name__ == "__main__":
    main()