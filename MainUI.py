import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from pathlib import Path
import time
import chessengine as ChessEngine
from chessengine import GameState, Move

BOARD_WIDTH = BOARD_HEIGHT = 576  # 9x9 board
DIMENSION = 9
SQUARE_SIZE = BOARD_HEIGHT // DIMENSION
IMAGES = {}

class ChessUI:
    def __init__(self, root):
        self.root = root
        self.root.title("9x9 Chess Game")
        self.root.configure(bg="#696561")
        self.game_state = GameState()
        self.valid_moves = self.game_state.getValidMoves()
        self.state = {"selected": (), "clicks": []}
        self.player_time = 600
        self.opponent_time = 600
        self.timer_running = False
        self.last_time_update = time.time()
        self.move_log = []
        self.move_index = -1
        self.first_move_made = False

        # Create canvas
        self.canvas = tk.Canvas(root, width=BOARD_WIDTH, height=BOARD_HEIGHT)
        self.canvas.pack(side="left")

        # Load images and initialize board
        if self.loadImages():
            self.drawBoard()
            self.drawPieces(self.game_state.board)
            self.canvas.bind("<Button-1>", lambda event: self.onSquareClick(event))
        else:
            self.root.destroy()
            return

        # Timer labels
        frame_sidebar = tk.Frame(root, bg="#f5dea9", width=200, height=180)
        frame_sidebar.pack(side="right")
        self.player_time_label = tk.Label(frame_sidebar, text="Player Time: 10:00", font=("Arial", 12), bg="#c27421", fg="#f5dea9")
        self.player_time_label.pack(pady=10)
        self.opponent_time_label = tk.Label(frame_sidebar, text="Opponent Time: 10:00", font=("Arial", 12), bg="#c27421", fg="#f5dea9")
        self.opponent_time_label.pack()

        # Buttons
        self.new_game_button = tk.Button(frame_sidebar, text="New Game", command=self.newGame, bg="#c27421", fg="#f5dea9")
        self.new_game_button.pack(pady=20)
        self.undo_button = tk.Button(frame_sidebar, text="Undo", command=self.undoMove, bg="#c27421", fg="#f5dea9")
        self.undo_button.pack(pady=10)
        self.redo_button = tk.Button(frame_sidebar, text="Redo", command=self.redoMove, bg="#c27421", fg="#f5dea9")
        self.redo_button.pack()

    def loadImages(self):
        """
        Load images for the pieces.
        """
        pieces = ['wP', 'wG', 'wV', 'wA', 'wB', 'wS', 'bP', 'bG', 'bV', 'bA', 'bB', 'bS']
        try:
            image_path = Path("C:/Users/Dharshan M Nadar/OneDrive/Documents/GitHub/ModernChessWarfare/images")
            for piece in pieces:
                img_path = image_path / f"{piece}.png"
                if img_path.exists():
                    img = Image.open(img_path)
                    img = img.resize((SQUARE_SIZE, SQUARE_SIZE), Image.Resampling.LANCZOS)
                    IMAGES[piece] = ImageTk.PhotoImage(img)
                else:
                    raise FileNotFoundError(f"Image not found: {img_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load chess pieces: {str(e)}")
            return False
        return True

    def drawBoard(self):
        """
        Draw the 9x9 chessboard.
        """
        colors = ["#f0d9b5", "#b58863"]
        for row in range(DIMENSION):
            for col in range(DIMENSION):
                color = colors[(row + col) % 2]
                self.canvas.create_rectangle(
                    col * SQUARE_SIZE, row * SQUARE_SIZE,
                    (col + 1) * SQUARE_SIZE, (row + 1) * SQUARE_SIZE,
                    fill=color, outline=""
                )

    def drawPieces(self, board):
        """
        Draw the pieces on the board.
        """
        self.canvas.delete("pieces")
        for row in range(DIMENSION):
            for col in range(DIMENSION):
                piece = board[row][col]
                if piece != "--" and piece in IMAGES:
                    self.canvas.create_image(
                        col * SQUARE_SIZE, row * SQUARE_SIZE,
                        image=IMAGES[piece], anchor="nw", tags="pieces"
                    )

    def highlightSquares(self, moves):
        """
        Highlight the squares for valid moves.
        """
        for move in moves:
            end_row, end_col = move.end_row, move.end_col
            self.canvas.create_rectangle(
                end_col * SQUARE_SIZE, end_row * SQUARE_SIZE,
                (end_col + 1) * SQUARE_SIZE, (end_row + 1) * SQUARE_SIZE,
                outline="#00FF00", width=3  # Green outline for valid moves
            )

    def onSquareClick(self, event):
        """
        Handle square clicks.
        """
        col = event.x // SQUARE_SIZE
        row = event.y // SQUARE_SIZE
        if not (0 <= row < DIMENSION and 0 <= col < DIMENSION):
            return
        square = (row, col)

        if self.state["selected"]:  # If a piece is already selected
            if square == self.state["selected"]:  # Clicked on the same piece again
                return  # Do nothing
            else:  # Clicked on a different square
                move = Move(self.state["selected"], square, self.game_state.board)
                for valid_move in self.valid_moves:
                    if move == valid_move:
                        self.game_state.makeMove(valid_move)
                        self.move_log.append(valid_move)
                        self.move_index += 1
                        if not self.first_move_made:
                            self.first_move_made = True
                            self.startTimer()
                        self.state["selected"] = ()  # Clear selection
                        self.state["clicks"] = []
                        self.valid_moves = self.game_state.getValidMoves()
                        self.drawBoard()
                        self.drawPieces(self.game_state.board)
                        return  # Exit after making a move

        # If no piece is selected, select the clicked piece
        piece = self.game_state.board[row][col]
        if piece != "--" and (piece[0] == 'w' if self.game_state.white_to_move else 'b'):
            self.state["selected"] = square
            self.state["clicks"] = [square]
            valid_moves = [move for move in self.valid_moves if move.start_row == row and move.start_col == col]
            self.drawBoard()
            self.drawPieces(self.game_state.board)
            self.highlightSquares(valid_moves)

    def startTimer(self):
        """
        Start the timer.
        """
        if not self.timer_running:
            self.timer_running = True
            self.last_time_update = time.time()
            self.updateTimer()

    def updateTimer(self):
        """
        Update the timer.
        """
        if self.timer_running:
            current_time = time.time()
            elapsed_time = current_time - self.last_time_update
            self.last_time_update = current_time
            if self.game_state.white_to_move:
                self.player_time -= elapsed_time
            else:
                self.opponent_time -= elapsed_time
            if self.player_time <= 0 or self.opponent_time <= 0:
                self.timer_running = False
                winner = "Black" if self.player_time <= 0 else "White"
                messagebox.showinfo("Game Over", f"Time's up! {winner} wins!")
            else:
                self.player_time_label.config(text=f"Player Time: {int(self.player_time // 60):02d}:{int(self.player_time % 60):02d}")
                self.opponent_time_label.config(text=f"Opponent Time: {int(self.opponent_time // 60):02d}:{int(self.opponent_time % 60):02d}")
                self.root.after(1000, self.updateTimer)

    def newGame(self):
        """
        Start a new game.
        """
        self.game_state = GameState()
        self.valid_moves = self.game_state.getValidMoves()
        self.state = {"selected": (), "clicks": []}
        self.player_time = 600
        self.opponent_time = 600
        self.timer_running = False
        self.last_time_update = time.time()
        self.move_log = []
        self.move_index = -1
        self.first_move_made = False
        self.drawBoard()
        self.drawPieces(self.game_state.board)
        self.player_time_label.config(text="Player Time: 10:00")
        self.opponent_time_label.config(text="Opponent Time: 10:00")

    def undoMove(self):
        """
        Undo the last move.
        """
        if self.move_index >= 0:
            self.game_state.undoMove()
            self.move_index -= 1
            self.valid_moves = self.game_state.getValidMoves()
            self.drawBoard()
            self.drawPieces(self.game_state.board)

    def redoMove(self):
        """
        Redo the last undone move.
        """
        if self.move_index < len(self.move_log) - 1:
            self.move_index += 1
            self.game_state.makeMove(self.move_log[self.move_index])
            self.valid_moves = self.game_state.getValidMoves()
            self.drawBoard()
            self.drawPieces(self.game_state.board)

def main():
    """
    Main function to run the game.
    """
    root = tk.Tk()
    ChessUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()