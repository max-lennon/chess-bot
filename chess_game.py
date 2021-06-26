from chess_piece import *
import copy
from pydispatch import Dispatcher

class ChessBoard:
    def __init__(self):
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.board_state = [[0 for _ in range(8)] for _ in range(8)]
        self.point_balance = 0
        self.white_turn = True

    def place(self, piece: ChessPiece):
        self.board[piece.starting_pos[0]][piece.starting_pos[1]] = piece

    def calc_moves(self, piece: ChessPiece):
        piece.reachable_squares = []
        if piece.long_range:
            found_limit = np.array([False for _ in range(len(piece.move_units))])
            dist = 1

            while not np.all(found_limit):
                for i in range(len(found_limit)):
                    if not found_limit[i]:
                        move = piece.position + piece.move_units[i] * dist
                        if self.verify_move(piece, move, capture=False):
                            pass
                        else:
                            self.verify_capture(piece, move)
                            found_limit[i] = True
                dist += 1

        elif piece.__class__ is Pawn:

            base_move = piece.position + piece.move_units[0]

            self.verify_move(piece, base_move, capture=False)

            if (piece.position == piece.starting_pos).all():
                self.verify_move(piece, base_move + piece.move_units[0], capture=False)

            self.verify_capture(piece, base_move + np.array([1, 0]))
            self.verify_capture(piece, base_move + np.array([-1, 0]))

        else:
            for vec in piece.move_units:
                move = piece.position + np.array(vec)
                self.verify_move(piece, move, capture=True)

    def verify_move(self, piece: ChessPiece, move: np.ndarray, capture: bool):
        if move[0] < 0 or move[1] < 0:
            return False
        try:
            if self.board[move[0]][move[1]] is None:
                piece.reachable_squares.append(move)
                return True
        except IndexError:
            return False

        if capture:
            return self.verify_capture(piece, move)

        return False

    def verify_capture(self, piece: ChessPiece, move: np.ndarray):
        # if move[0] < 0 or move[1] < 0:
        #     return False
        try:
            target_piece = self.board[move[0]][move[1]]
            if isinstance(target_piece, ChessPiece):
                if piece.white ^ target_piece.white:
                    piece.reachable_squares.append(move)
                    return True
                return False
        except IndexError:
            return False
        return False

    def verify_safe(self, piece: ChessPiece, move: np.ndarray):
        pass

    def move_piece(self, piece: ChessPiece, move: np.ndarray):
        if np.asarray(piece.reachable_squares).__contains__(move):
            prev_pos = piece.position
            self.board[move[0]][move[1]] = piece
            self.board[prev_pos[0]][prev_pos[1]] = None
            piece.position = move
            self.white_turn = not self.white_turn

    def capture_piece(self, piece: ChessPiece, move: np.ndarray):
        target_piece = self.board[move[0]][move[1]]
        if np.asarray(piece.reachable_squares).__contains__(move):
            self.point_balance -= target_piece.point_value
            prev_pos = piece.position
            self.board[move[0]][move[1]] = piece
            self.board[prev_pos[0]][prev_pos[1]] = None
            piece.position = move
            self.white_turn = not self.white_turn


class Player(Dispatcher):

    _events_ = ['turn', 'capture', 'check', 'checkmate', 'stalemate']

    def on_turn(self):
        return


















# # TODO: Implement move legality based on checking the king
# class ChessPiece:
#     def __init__(self, point_value, starting_pos, long_range, white):
#         self.point_value = point_value
#         self.starting_pos = starting_pos
#         self.position = starting_pos
#         self.reachable_squares = []
#         self.move_units = []
#         self.long_range = long_range
#         self.white = white
#
#     def verify_move(self, square, capture=False):
#         try:
#             if board[square[0]][square[1]] is None:
#                 return True
#         except IndexError:
#             return False
#
#         if capture:
#             return self.verify_capture(square)
#
#         return False
#
#     def verify_capture(self, square):
#         try:
#             square_occupant = board[square[0]][square[1]]
#         except IndexError:
#             return False
#         if square_occupant is ChessPiece:
#             return self.white ^ square_occupant.white
#         return False
#
#
# # TODO: Implement en passant rule for pawns
# class Pawn(ChessPiece):
#     def __init__(self, starting_pos, white):
#         super().__init__(point_value=1, starting_pos=starting_pos, long_range=False, white=white)
#         if self.white:
#             self.move_units = [np.array([1, 0])]
#         else:
#             self.move_units = [np.array([-1, 0])]
#
#     def calc_moves(self):
#         self.reachable_squares = []
#
#         move = self.position + self.move_units[0]
#         if self.verify_move(move):
#             self.reachable_squares.append(move)
#
#         start_move = self.position + 2 * self.move_units[0]
#         if self.position == self.starting_pos and self.verify_move(start_move):
#             self.reachable_squares.append(start_move)
#
#         capture1 = move + np.array([0, 1])
#         if self.verify_capture(capture1):
#             self.reachable_squares.append(capture1)
#
#         capture2 = move + np.array([0, -1])
#         if self.verify_capture(capture2):
#             self.reachable_squares.append(capture2)
#
#
# class Bishop(ChessPiece):
#     def __init__(self, starting_pos, white):
#         super().__init__(point_value=3, starting_pos=starting_pos, long_range=True, white=white)
#         self.move_units = [np.array(vec) for vec in [[1, 1], [1, -1], [-1, 1], [-1, -1]]]
#
#     def calc_moves(self):
#         self.reachable_squares = []
#
#         found_limit = np.array([False for _ in range(len(self.move_units))])
#         dist = 1
#
#         while not np.all(found_limit):
#             for i in range(len(found_limit)):
#                 if not found_limit[i]:
#                     move = self.position + self.move_units[i] * dist
#                     if self.verify_move(move):
#                         self.reachable_squares.append(move)
#                     else:
#                         if self.verify_capture(move):
#                             self.reachable_squares.append(move)
#                         found_limit[i] = True
#             dist += 1
#
#
# class Knight(ChessPiece):
#     def __init__(self, starting_pos, white):
#         super().__init__(point_value=3, starting_pos=starting_pos, long_range=False, white=white)
#         self.move_units = [[1, 2], [1, -2], [-1, 2], [-1, -2], [2, 1], [2, -1], [-2, 1], [-2, -1]]
#
#     def calc_moves(self):
#         self.reachable_squares = []
#
#         for vec in self.move_units:
#             move = self.position + np.array(vec)
#             if self.verify_move(move, capture=True):
#                 self.reachable_squares.append(move)
#
#
# class Rook(ChessPiece):
#     def __init__(self, starting_pos, white):
#         super().__init__(point_value=5, starting_pos=starting_pos, long_range=True, white=white)
#         self.move_units = [np.array(vec) for vec in [[0, 1], [0, -1], [1, 0], [-1, 0]]]
#
#     def calc_moves(self):
#         self.reachable_squares = []
#
#         found_limit = np.array([False for _ in range(len(self.move_units))])
#         dist = 1
#
#         while not np.all(found_limit):
#             for i in range(len(found_limit)):
#                 if not found_limit[i]:
#                     move = self.position + self.move_units[i] * dist
#                     if self.verify_move(move):
#                         self.reachable_squares.append(move)
#                     else:
#                         if self.verify_capture(move):
#                             self.reachable_squares.append(move)
#                         found_limit[i] = True
#             dist += 1
#
#
# class Queen(ChessPiece):
#     def __init__(self, starting_pos, white):
#         super().__init__(point_value=9, starting_pos=starting_pos, long_range=True, white=white)
#         self.move_units = [np.array(vec) for vec in
#                            [[0, 1], [0, -1], [1, 0], [-1, 0], [1, 1], [1, -1], [-1, 1], [-1, -1]]]
#
#     def calc_moves(self):
#         self.reachable_squares = []
#
#         found_limit = np.array([False for _ in range(len(self.move_units))])
#         dist = 1
#
#         while not np.all(found_limit):
#             for i in range(len(found_limit)):
#                 if not found_limit[i]:
#                     move = self.position + self.move_units[i] * dist
#                     if self.verify_move(move):
#                         self.reachable_squares.append(move)
#                     else:
#                         if self.verify_capture(move):
#                             self.reachable_squares.append(move)
#                         found_limit[i] = True
#             dist += 1
#
#
# class King(ChessPiece):
#     def __init__(self, starting_pos, white):
#         super().__init__(point_value=np.inf, starting_pos=starting_pos, long_range=False, white=white)
#         self.move_units = [np.array(vec) for vec in
#                            [[0, 1], [0, -1], [1, 0], [-1, 0], [1, 1], [1, -1], [-1, 1], [-1, -1]]]
#
#     def calc_moves(self):
#         self.reachable_squares = []
#
#         for vec in self.move_units:
#             move = self.position + vec
#             if self.verify_move(move, capture=True):
#                 self.reachable_squares.append(move)
