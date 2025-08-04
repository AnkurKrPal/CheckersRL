import pygame
import time

# Initialize Pygame first to use its functions
pygame.init()

# -----------------------------------------------------------------------------
# --- CONSTANTS ---
# This section replaces the 'constants.py' file
# -----------------------------------------------------------------------------

# --- Dimensions ---
WIDTH, HEIGHT = 800, 800
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS

# --- RGB Colors ---
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREY = (128, 128, 128)

# --- Images ---
# The crown image is used to denote a "King" piece.
# Ensure you have an 'assets' folder with 'crown.png' in it.
try:
    CROWN = pygame.transform.scale(pygame.image.load('assets/crown.png'), (44, 25))
except pygame.error as e:
    print("Error loading crown image: 'assets/crown.png'. Please ensure the file exists.")
    print("A default shape will be used for kings instead.")
    CROWN = None


# -----------------------------------------------------------------------------
# --- PIECE CLASS ---
# This section replaces the 'piece.py' file
# -----------------------------------------------------------------------------

class Piece:
    """
    Represents a single checker piece on the board.
    """
    PADDING = 15
    OUTLINE = 2

    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color
        self.king = False
        self.x = 0
        self.y = 0
        self.calc_pos()

    def calc_pos(self):
        """Calculates the x, y pixel coordinates based on row and col."""
        self.x = SQUARE_SIZE * self.col + SQUARE_SIZE // 2
        self.y = SQUARE_SIZE * self.row + SQUARE_SIZE // 2

    def make_king(self):
        """Makes the current piece a king."""
        self.king = True

    def draw(self, win):
        """Draws the piece on the window."""
        radius = SQUARE_SIZE // 2 - self.PADDING
        pygame.draw.circle(win, GREY, (self.x, self.y), radius + self.OUTLINE)
        pygame.draw.circle(win, self.color, (self.x, self.y), radius)
        if self.king:
            if CROWN:
                win.blit(CROWN, (self.x - CROWN.get_width() // 2, self.y - CROWN.get_height() // 2))
            else: # Fallback if image not found
                pygame.draw.circle(win, BLUE, (self.x, self.y), radius // 2)


    def move(self, row, col):
        """Updates the piece's row and column and recalculates pixel position."""
        self.row = row
        self.col = col
        self.calc_pos()

    def __repr__(self):
        """String representation of the piece, useful for debugging."""
        return str(self.color)

# -----------------------------------------------------------------------------
# --- BOARD CLASS ---
# This section replaces the 'board.py' file
# -----------------------------------------------------------------------------

class Board:
    """
    Manages the board's internal data structure, pieces, and game logic for moves.
    """
    def __init__(self):
        self.board = []
        self.red_left = self.white_left = 12
        self.red_kings = self.white_kings = 0
        self.create_board()

    def draw_squares(self, win):
        """Draws the checkerboard pattern."""
        win.fill(BLACK)
        for row in range(ROWS):
            for col in range(row % 2, COLS, 2):
                pygame.draw.rect(win, RED, (row * SQUARE_SIZE, col * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    def move(self, piece, row, col):
        """Moves a piece and promotes it to a king if necessary."""
        self.board[piece.row][piece.col], self.board[row][col] = self.board[row][col], self.board[piece.row][piece.col]
        piece.move(row, col)

        if row == ROWS - 1 or row == 0:
            if not piece.king:
                piece.make_king()
                if piece.color == WHITE:
                    self.white_kings += 1
                else:
                    self.red_kings += 1
    
    def get_piece(self, row, col):
        """Returns the piece object at a given row and col."""
        return self.board[row][col]

    def create_board(self):
        """Initializes the board with pieces in starting positions."""
        for row in range(ROWS):
            self.board.append([])
            for col in range(COLS):
                if col % 2 == ((row + 1) % 2):
                    if row < 3:
                        self.board[row].append(Piece(row, col, WHITE))
                    elif row > 4:
                        self.board[row].append(Piece(row, col, RED))
                    else:
                        self.board[row].append(0)
                else:
                    self.board[row].append(0)

    def draw(self, win):
        """Draws the entire board, including squares and pieces."""
        self.draw_squares(win)
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece != 0:
                    piece.draw(win)

    def remove(self, pieces):
        """Removes captured pieces from the board."""
        for piece in pieces:
            self.board[piece.row][piece.col] = 0
            if piece != 0:
                if piece.color == RED:
                    self.red_left -= 1
                else:
                    self.white_left -= 1
    
    def winner(self):
        """Determines the winner."""
        if self.red_left <= 0:
            return WHITE
        elif self.white_left <= 0:
            return RED
        
        return None

    def get_valid_moves(self, piece):
        """Calculates all valid moves for a given piece."""
        moves = {}
        left = piece.col - 1
        right = piece.col + 1
        row = piece.row

        if piece.color == RED or piece.king:
            moves.update(self._traverse_left(row - 1, max(row - 3, -1), -1, piece.color, left))
            moves.update(self._traverse_right(row - 1, max(row - 3, -1), -1, piece.color, right))
        
        if piece.color == WHITE or piece.king:
            moves.update(self._traverse_left(row + 1, min(row + 3, ROWS), 1, piece.color, left))
            moves.update(self._traverse_right(row + 1, min(row + 3, ROWS), 1, piece.color, right))

        return moves

    def _traverse_left(self, start, stop, step, color, left, skipped=[]):
        """Helper for recursively finding valid moves to the left."""
        moves = {}
        last = []
        for r in range(start, stop, step):
            if left < 0:
                break
            
            current = self.board[r][left]
            if current == 0:
                if skipped and not last:
                    break
                elif skipped:
                    moves[(r, left)] = last + skipped
                else:
                    moves[(r, left)] = last
                
                if last:
                    if step == -1:
                        row = max(r-3, -1)
                    else:
                        row = min(r+3, ROWS)
                    moves.update(self._traverse_left(r+step, row, step, color, left-1, skipped=last))
                    moves.update(self._traverse_right(r+step, row, step, color, left+1, skipped=last))
                break
            elif current.color == color:
                break
            else:
                last = [current]

            left -= 1
        
        return moves

    def _traverse_right(self, start, stop, step, color, right, skipped=[]):
        """Helper for recursively finding valid moves to the right."""
        moves = {}
        last = []
        for r in range(start, stop, step):
            if right >= COLS:
                break
            
            current = self.board[r][right]
            if current == 0:
                if skipped and not last:
                    break
                elif skipped:
                    moves[(r,right)] = last + skipped
                else:
                    moves[(r, right)] = last
                
                if last:
                    if step == -1:
                        row = max(r-3, -1)
                    else:
                        row = min(r+3, ROWS)
                    moves.update(self._traverse_left(r+step, row, step, color, right-1,skipped=last))
                    moves.update(self._traverse_right(r+step, row, step, color, right+1,skipped=last))
                break
            elif current.color == color:
                break
            else:
                last = [current]

            right += 1
        
        return moves

# -----------------------------------------------------------------------------
# --- GAME CLASS ---
# This section replaces the 'game.py' file
# -----------------------------------------------------------------------------

class Game:
    """
    Main controller for the game. Handles turns, selection, and game state.
    """
    def __init__(self, win):
        self._init()
        self.win = win

    def update(self):
        """Updates the display with the current board state."""
        self.board.draw(self.win)
        self.draw_valid_moves(self.valid_moves)
        pygame.display.update()

    def _init(self):
        """Initializes a new game."""
        self.selected = None
        self.board = Board()
        self.turn = RED
        self.valid_moves = {}

    def winner(self):
        """Returns the winner of the game, if there is one."""
        return self.board.winner()

    def reset(self):
        """Resets the game to the initial state."""
        self._init()

    def select(self, row, col):
        """Selects a piece or attempts to move to a selected square."""
        if self.selected:
            result = self._move(row, col)
            if not result:
                self.selected = None
                self.select(row, col)
        
        piece = self.board.get_piece(row, col)
        if piece != 0 and piece.color == self.turn:
            self.selected = piece
            self.valid_moves = self.board.get_valid_moves(piece)
            return True
            
        return False

    def _move(self, row, col):
        """Moves a selected piece to a new row and column."""
        if self.selected and (row, col) in self.valid_moves:
            piece_to_move = self.board.get_piece(self.selected.row, self.selected.col)
            skipped = self.valid_moves[(row, col)]
            self.board.move(piece_to_move, row, col)
            if skipped:
                self.board.remove(skipped)
            self.change_turn()
            return True
        return False

    def draw_valid_moves(self, moves):
        """Draws blue circles on squares that are valid moves."""
        for move in moves:
            row, col = move
            pygame.draw.circle(self.win, BLUE, (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2), 15)

    def change_turn(self):
        """Changes the current player's turn."""
        self.valid_moves = {}
        if self.turn == RED:
            self.turn = WHITE
        else:
            self.turn = RED

# -----------------------------------------------------------------------------
# --- MAIN GAME LOOP ---
# This section replaces the 'main.py' file
# -----------------------------------------------------------------------------

FPS = 60

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Checkers')

def get_row_col_from_mouse(pos):
    """Converts mouse (x, y) coordinates to board (row, col) coordinates."""
    x, y = pos
    row = y // SQUARE_SIZE
    col = x // SQUARE_SIZE
    return row, col

def main():
    """Main function to run the game."""
    run = True
    clock = pygame.time.Clock()
    game = Game(WIN)

    while run:
        clock.tick(FPS)

        if game.winner() is not None:
            winner_color_val = game.winner()
            winner_color_name = "Red" if winner_color_val == RED else "White"
            
            # Display winner message on screen
            font = pygame.font.SysFont("comicsans", 80)
            text = font.render(f"{winner_color_name} Wins!", True, BLUE)
            WIN.blit(text, (WIDTH/2 - text.get_width()/2, HEIGHT/2 - text.get_height()/2))
            pygame.display.update()
            
            print(f"Game Over: {winner_color_name} wins!")
            time.sleep(5) # Pause for 5 seconds before closing
            run = False
            continue

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                row, col = get_row_col_from_mouse(pos)
                game.select(row, col)

        game.update()

    pygame.quit()

# This ensures the main function runs only when the script is executed directly
if __name__ == '__main__':
    main()