from chess_piece import *
import copy
from pydispatch import Dispatcher

class ChessBoard:
    def __init__(self):
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.board_state = np.zeros((8, 8))
        self.point_balance = 0
        self.white_turn = True

    def place(self, piece: ChessPiece):
        start_col = piece.starting_pos[0]
        start_row = piece.starting_pos[1]
        self.board[start_col][start_row] = piece
        self.board_state[(start_col, start_row)] = piece.piece_type
        print(self.board_state)

    def calc_moves(self, piece: ChessPiece, game_state: np.ndarray):
        reachable_squares = []
        if piece.long_range:
            found_limit = np.array([False for _ in range(len(piece.move_units))])
            dist = 1

            while not np.all(found_limit):
                for i in range(len(found_limit)):
                    if not found_limit[i]:
                        move = piece.position + piece.move_units[i] * dist
                        open, legal = self.verify_move(piece, move, game_state, capture=False)
                        if open and legal:
                            reachable_squares.append(move)
                        else:
                            if all(self.verify_capture(piece, move, game_state)):
                                reachable_squares.append(move)
                            if not open:
                                found_limit[i] = True
                dist += 1

        elif piece.__class__ is Pawn:

            base_move = piece.position + piece.move_units[0]

            if all(self.verify_move(piece, base_move, game_state, capture=False)):
                reachable_squares.append(base_move)

            if (piece.position == piece.starting_pos).all() and \
                    all(self.verify_move(piece, base_move + piece.move_units[0], game_state, capture=False)):
                reachable_squares.append(base_move + piece.move_units[0])

            if all(self.verify_capture(piece, base_move + np.array([1, 0]), game_state)):
                reachable_squares.append(base_move + np.array([1, 0]))
            if all(self.verify_capture(piece, base_move + np.array([-1, 0]), game_state)):
                reachable_squares.append(base_move + np.array([-1, 0]))

        else:
            for vec in piece.move_units:
                move = piece.position + np.array(vec)
                if all(self.verify_move(piece, move, game_state, capture=True)):
                    reachable_squares.append(move)

            if piece.__class__ is King:
                print(1)
                if piece.castle_possible[0]:
                    print(2)
                    if all([self.board_state[i][piece.position[1]] == 0 for i in [1,2,3]]):
                        print(3)
                        if self.verify_safe(piece, piece.position):
                            print(4)
                            if self.verify_safe(piece, np.array([2,piece.position[0]])):
                                print(5)
                                if self.verify_safe(piece, np.array([3,piece.position[1]])):
                                    print(6)
                                    reachable_squares.append(np.array([2,piece.position[1]]))
                    else:
                        print([self.board_state[i][piece.position[1]] for i in [1,2,3]])
                if piece.castle_possible[1]:
                    if all([self.board_state[i][piece.position[1]] == 0 for i in [5,6]]):
                        if self.verify_safe(piece, piece.position):
                            if self.verify_safe(piece, np.array([6,piece.position[1]])):
                                if self.verify_safe(piece, np.array([5,piece.position[1]])):
                                    reachable_squares.append(np.array([6,piece.position[1]]))


        return reachable_squares

    def verify_move(self, piece: ChessPiece, move: np.ndarray, game_state: np.ndarray, capture: bool):
        if move[0] < 0 or move[1] < 0:
            return False, False
        try:
            if game_state[move[0], move[1]] == 0:
                return True, self.verify_safe(piece, move)
        except IndexError:
            return False, False

        if capture:
            return self.verify_capture(piece, move, game_state)

        return False, False

    def verify_capture(self, piece: ChessPiece, move: np.ndarray, game_state: np.ndarray):
        if move[0] < 0 or move[1] < 0:
            return False, False
        try:
            target_piece = game_state[move[0], move[1]]
            if target_piece != 0:
                return True, piece.piece_type * target_piece < 0 and self.verify_safe(piece, move)
        except IndexError:
            return False, False
        return False, False

    def verify_safe(self, piece: ChessPiece, move: np.ndarray):

        # print("Checking for checking...")

        test_board = self.board_state.copy()
        # print(piece.move_units)
        test_board[piece.position[0]][piece.position[1]] = 0
        test_board[move[0]][move[1]] = piece.piece_type

        # print(test_board)

        if piece.white:
            pawn_value = -1
            bishop_value = -2
            knight_value = -3
            rook_value = -4
            queen_value = -5
            king_value = -6
        else:
            pawn_value = 1
            bishop_value = 2
            knight_value = 3
            rook_value = 4
            queen_value = 5
            king_value = 6

        test_units = [np.array(vec) for vec in [[0, 1], [0, -1], [1, 0], [-1, 0], [1, 1], [1, -1], [-1, 1], [-1, -1]]]

        knight_units = [[1, 2], [1, -2], [-1, 2], [-1, -2], [2, 1], [2, -1], [-2, 1], [-2, -1]]

        try:
            king_pos = np.array([arr[0] for arr in np.where(test_board == -1 * king_value)])
        except Exception:
            print(test_board)
            print(np.where(test_board == -1 * king_value))
            print("safety exception")
            return False

        print(king_pos)

        for diag in [np.array([-1, -1]), np.array([1, -1])]:
            # print("For loop")
            move = king_pos + diag * pawn_value
            try:
                if test_board[move[0], move[1]] == pawn_value:
                    # print("Condition 1")
                    return False
            except Exception:
                print("Error!")
                pass

        found_limit = np.array([False for _ in range(len(test_units))])
        # print(found_limit)
        dist = 1

        while not np.all(found_limit):
            for i, unit in enumerate(test_units):

                diag = np.prod(unit) != 0

                if not found_limit[i]:
                    move = king_pos + unit * dist

                    if move[0] < 0 or move[1] < 0:
                        found_limit[i] = True
                        continue

                    if dist == 1:
                        try:
                            if test_board[move[0], move[1]] == king_value:
                                return False
                        except IndexError:
                            found_limit[i] = True
                            continue

                    try:
                        if test_board[move[0], move[1]] == 0:
                            continue
                        elif test_board[move[0], move[1]] * piece.piece_type > 0:
                            found_limit[i] = True
                        else:
                            if test_board[move[0], move[1]] == queen_value:
                                # print("Condition 2")
                                return False
                            elif not diag and test_board[move[0], move[1]] == rook_value:
                                # print("Condition 3")
                                return False
                            elif diag and test_board[move[0], move[1]] == bishop_value:
                                # print("Condition 4")
                                return False
                            found_limit[i] = True
                    except IndexError:
                        found_limit[i] = True
            dist += 1
            # print(dist)

        for unit in knight_units:
            move = king_pos + unit
            if move[0] < 0 or move[1] < 0:
                continue
            try:
                if test_board[move[0], move[1]] == knight_value:
                    # print("Condition 5")
                    return False
            except IndexError:
                continue

        # print("It's safe.")
        return True

    def move_piece(self, piece: ChessPiece, move: np.ndarray):
        white_turn = self.white_turn
        if piece.white == self.white_turn:
            if True or np.asarray(piece.reachable_squares).__contains__(move):
                prev_pos = piece.position
                self.board[move[0]][move[1]] = piece
                self.board[prev_pos[0]][prev_pos[1]] = None
                self.board_state[move[0], move[1]] = piece.piece_type
                self.board_state[prev_pos[0], prev_pos[1]] = 0
                if piece.__class__ is King:
                    piece.castle_available = [False, False]
                    if piece.position[0] - move[0] < -1:
                        self.move_piece(self.board[7][piece.position[1]], np.array([5, piece.position[1]]))
                    elif piece.position[0] - move[0] > 1:
                        self.move_piece(self.board[0][piece.position[1]], np.array([2, piece.position[1]]))
                elif piece.__class__ is Rook:
                    if piece.white:
                        if self.board_state[4][0] == 6:
                            self.board[4][0].castle_possible[int(piece.starting_pos[0]/7)] = False
                    else:
                        if self.board[4][7] == -6:
                            self.board[4][7].castle_possible[int(piece.starting_pos[0]/7)] = False
                piece.position = move
                self.white_turn = not white_turn
                return True
        return False

    def capture_piece(self, piece: ChessPiece, move: np.ndarray):
        if piece.white == self.white_turn:
            target_piece = self.board[move[0]][move[1]]
            if np.asarray(piece.reachable_squares).__contains__(move):
                self.point_balance -= target_piece.point_value
                prev_pos = piece.position
                self.board[move[0]][move[1]] = piece
                self.board[prev_pos[0]][prev_pos[1]] = None
                self.board_state[move[0], move[1]] = piece.piece_type
                self.board_state[prev_pos[0], prev_pos[1]] = 0
                if piece.__class__ is King:
                    piece.castle_available = [False, False]
                elif piece.__class__ is Rook:
                    if piece.white:
                        if self.board[4][0] is ChessPiece and self.board[4][0].__class__ is King:
                            self.board[4][0].castle_possible[int(piece.starting_pos[0] / 7)] = False
                    else:
                        if self.board[4][7] is ChessPiece and self.board[4][7].__class__ is King:
                            self.board[4][7].castle_possible[int(piece.starting_pos[0] / 7)] = False
                piece.position = move
                self.white_turn = not self.white_turn
                return True
        return False


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
