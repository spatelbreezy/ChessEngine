# Main driver file. 
# Handles user input and displays the current game state. 
import Engine 
import pygame as p

WIDTH = HEIGHT = 512
DIMENSION = 8 
SQ_SIZE = HEIGHT // DIMENSION #size of each board square
MAX_FPS = 15 
IMAGES = {}

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
    load_images()
    running = True
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
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