# ChessEngine
<p>A fully capable chess engine that allows you to play Player vs Player, and Player Vs AI. </p>
<p>By default it is PLAYER VS. AI
If you wanna play PLAYER VS. PLAYER, set player_two var to True on line 42 of main.py</p>
<p>Possible future improvements:<br>
UI improvements:<br>
-Menu to select AI/Human<br>
-Flip board options (display from black perspective)</p>
<p>Engine improvements:<br>
-Add 50 move draw and 3 move repeating draw rule<br>
-Move ordering - look at checks, captures and threats first, prioritize castling/king safety, look at pawn moves last (this will improve alpha-beta pruning). Also start with moves that previously scored higher (will also improve pruning).<br>
-Calculate both players moves given a position<br>
-Change move calculation to make it more efficient. Instead of recalculating all moves, start with moves from previous board and change based on last move made<br>
-Use a numpy array instead of 2d list of strings or store the board differently (**Major change)<br> 
-Hash board positions already visited to improve computation time for transpositions<br>
-If move is a capture move, even at max depth, continue evaluating until no captures remain
-Add multiprocessing,threading to able to do things while the AI is thinking<br></p>
