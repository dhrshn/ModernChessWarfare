class GameState:
    def __init__(self):
        """
        Board is a 9x9 2D list. Each element has 2 characters.
        The first character represents the color: 'w' or 'b'.
        The second character represents the piece type.
        "--" represents an empty square.
        """
        self.board = [
            ["bA", "bB", "bV", "bS", "bP", "bG", "bV", "bB", "bA"],
            ["bS", "bS", "bS", "bS", "bS", "bS", "bS", "bS", "bS"],
            ["--", "--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--", "--"],
            ["wS", "wS", "wS", "wS", "wS", "wS", "wS", "wS", "wS"],
            ["wA", "wB", "wV", "wS", "wP", "wG", "wV", "wB", "wA"]
        ]
        self.moveFunctions = {
            "P": self.getPresidentMoves,
            "G": self.getGeneralMoves,
            "V": self.getViceGeneralMoves,
            "A": self.getAirMarshalMoves,
            "B": self.getNavySealMoves,
            "S": self.getSoldierMoves,
            "K": self.getArmyBattalionMoves
        }
        self.white_to_move = True
        self.move_log = []
        self.white_president_location = (8, 4)
        self.black_president_location = (0, 4)
        self.checkmate = False
        self.stalemate = False
        self.in_check = False
        self.pins = []
        self.checks = []

    def makeMove(self, move):
        """
        Execute a move.
        """
        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.move_log.append(move)
        self.white_to_move = not self.white_to_move
        # Update president location
        if move.piece_moved == "wP":
            self.white_president_location = (move.end_row, move.end_col)
        elif move.piece_moved == "bP":
            self.black_president_location = (move.end_row, move.end_col)

    def undoMove(self):
        """
        Undo the last move.
        """
        if len(self.move_log) != 0:
            move = self.move_log.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.white_to_move = not self.white_to_move
            # Update president location
            if move.piece_moved == "wP":
                self.white_president_location = (move.start_row, move.start_col)
            elif move.piece_moved == "bP":
                self.black_president_location = (move.start_row, move.start_col)

    def getValidMoves(self):
        """
        Get all valid moves considering checks.
        """
        moves = self.getAllPossibleMoves()
        return moves

    def getAllPossibleMoves(self):
        """
        Get all possible moves without considering checks.
        """
        moves = []
        for row in range(9):
            for col in range(9):
                piece = self.board[row][col]
                if piece != "--" and (piece[0] == 'w' if self.white_to_move else 'b'):
                    self.moveFunctions[piece[1]](row, col, moves)
        return moves

    def getPresidentMoves(self, row, col, moves):
        """
        President moves one step in any direction.
        """
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        for d in directions:
            end_row = row + d[0]
            end_col = col + d[1]
            if 0 <= end_row < 9 and 0 <= end_col < 9:
                end_piece = self.board[end_row][end_col]
                if end_piece == "--" or end_piece[0] != self.board[row][col][0]:
                    moves.append(Move((row, col), (end_row, end_col), self.board))

    def getGeneralMoves(self, row, col, moves):
        """
        General moves: N, NE, NW, E, and one step S.
        """
        directions = [(-1, 0), (-1, 1), (-1, -1), (0, 1)]
        for d in directions:
            for i in range(1, 9):
                end_row = row + d[0] * i
                end_col = col + d[1] * i
                if 0 <= end_row < 9 and 0 <= end_col < 9:
                    end_piece = self.board[end_row][end_col]
                    if end_piece == "--":
                        moves.append(Move((row, col), (end_row, end_col), self.board))
                    elif end_piece[0] != self.board[row][col][0]:
                        moves.append(Move((row, col), (end_row, end_col), self.board))
                        break
                    else:
                        break
        # One step S
        end_row = row + 1
        end_col = col
        if 0 <= end_row < 9 and 0 <= end_col < 9:
            end_piece = self.board[end_row][end_col]
            if end_piece == "--" or end_piece[0] != self.board[row][col][0]:
                moves.append(Move((row, col), (end_row, end_col), self.board))

    def getViceGeneralMoves(self, row, col, moves):
        """
        Vice-General moves: S, SE, SW, E, W, and one step N.
        """
        directions = [(1, 0), (1, 1), (1, -1), (0, 1), (0, -1)]
        for d in directions:
            for i in range(1, 9):
                end_row = row + d[0] * i
                end_col = col + d[1] * i
                if 0 <= end_row < 9 and 0 <= end_col < 9:
                    end_piece = self.board[end_row][end_col]
                    if end_piece == "--":
                        moves.append(Move((row, col), (end_row, end_col), self.board))
                    elif end_piece[0] != self.board[row][col][0]:
                        moves.append(Move((row, col), (end_row, end_col), self.board))
                        break
                    else:
                        break
        # One step N
        end_row = row - 1
        end_col = col
        if 0 <= end_row < 9 and 0 <= end_col < 9:
            end_piece = self.board[end_row][end_col]
            if end_piece == "--" or end_piece[0] != self.board[row][col][0]:
                moves.append(Move((row, col), (end_row, end_col), self.board))

    def getAirMarshalMoves(self, row, col, moves):
        """
        Air Marshal moves: NE-W, SE-W, and N.
        """
        directions = [(-1, 1), (1, 1), (-1, 0)]
        for d in directions:
            for i in range(1, 9):
                end_row = row + d[0] * i
                end_col = col + d[1] * i
                if 0 <= end_row < 9 and 0 <= end_col < 9:
                    end_piece = self.board[end_row][end_col]
                    if end_piece == "--":
                        moves.append(Move((row, col), (end_row, end_col), self.board))
                    elif end_piece[0] != self.board[row][col][0]:
                        moves.append(Move((row, col), (end_row, end_col), self.board))
                        break
                    else:
                        break

    def getNavySealMoves(self, row, col, moves):
        """
        Navy Seal moves: 2 steps NE-W, SE-W, SW-W, NW-W.
        """
        directions = [(-2, 2), (2, 2), (2, -2), (-2, -2)]
        for d in directions:
            end_row = row + d[0]
            end_col = col + d[1]
            if 0 <= end_row < 9 and 0 <= end_col < 9:
                end_piece = self.board[end_row][end_col]
                if end_piece == "--" or end_piece[0] != self.board[row][col][0]:
                    moves.append(Move((row, col), (end_row, end_col), self.board))

    def getArmyBattalionMoves(self, row, col, moves):
        """
        Army Battalion moves: N, S, E, W.
        """
        directions = [(-1, 0), (1, 0), (0, 1), (0, -1)]
        for d in directions:
            for i in range(1, 9):
                end_row = row + d[0] * i
                end_col = col + d[1] * i
                if 0 <= end_row < 9 and 0 <= end_col < 9:
                    end_piece = self.board[end_row][end_col]
                    if end_piece == "--":
                        moves.append(Move((row, col), (end_row, end_col), self.board))
                    elif end_piece[0] != self.board[row][col][0]:
                        moves.append(Move((row, col), (end_row, end_col), self.board))
                        break
                    else:
                        break

    def getSoldierMoves(self, row, col, moves):
        """
        Soldier (Pawn) moves.
        """
        if self.white_to_move:
            if row - 1 >= 0 and self.board[row - 1][col] == "--":
                moves.append(Move((row, col), (row - 1, col), self.board))
                if row == 7 and self.board[row - 2][col] == "--":
                    moves.append(Move((row, col), (row - 2, col), self.board))
            if row - 1 >= 0 and col - 1 >= 0:
                if self.board[row - 1][col - 1][0] == 'b':
                    moves.append(Move((row, col), (row - 1, col - 1), self.board))
            if row - 1 >= 0 and col + 1 < 9:
                if self.board[row - 1][col + 1][0] == 'b':
                    moves.append(Move((row, col), (row - 1, col + 1), self.board))
        else:
            if row + 1 < 9 and self.board[row + 1][col] == "--":
                moves.append(Move((row, col), (row + 1, col), self.board))
                if row == 1 and self.board[row + 2][col] == "--":
                    moves.append(Move((row, col), (row + 2, col), self.board))
            if row + 1 < 9 and col - 1 >= 0:
                if self.board[row + 1][col - 1][0] == 'w':
                    moves.append(Move((row, col), (row + 1, col - 1), self.board))
            if row + 1 < 9 and col + 1 < 9:
                if self.board[row + 1][col + 1][0] == 'w':
                    moves.append(Move((row, col), (row + 1, col + 1), self.board))


class Move:
    def __init__(self, start_sq, end_sq, board):
        self.start_row = start_sq[0]
        self.start_col = start_sq[1]
        self.end_row = end_sq[0]
        self.end_col = end_sq[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]
        self.moveID = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False