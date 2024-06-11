# Main driver file. 
# Handles user input and displays the current game state. 
import Engine 
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
    load_images()
    running = True
    selected_sq = () #default is no selected square, stores a tuple (row,col)
    player_clicks = [] #keeps track of clicks, 2 tuples with start(x,y) and end(x,y)


    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            #mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
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
                    if move in valid_moves:
                        gs.make_move(move)
                        move_made = True
                    #resets user clicks
                    selected_sq = () 
                    player_clicks = []
            #key handlers
            elif e.type == p.KEYDOWN:
                if e.key  == p.K_z: #undo when 'z' is pressed
                    gs.undo_move()
                    move_made = True
        if move_made:
            valid_moves = gs.get_valid_moves()
            move_made = False

        draw_gamestate(screen, gs)
        clock.tick(MAX_FPS)
        p.display.flip()

#Draws the given game state 
#Responsible for all graphics witihin a current game state!
def draw_gamestate(screen, gs):
    draw_board(screen) 
    draw_pieces(screen, gs.board) 
    

#Draws squares on board    
def draw_board(screen):
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

#if imported, this will still work!
if __name__ == "__main__":
    main()