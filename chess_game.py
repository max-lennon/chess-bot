import numpy as np

board = [[None for i in range(8)] for j in range(8)]


# TODO: Implement move legality based on checking the king
class ChessPiece:
    def __init__(self, point_value, starting_pos, white):
        self.point_value = point_value
        self.starting_pos = starting_pos
        self.position = starting_pos
        self.reachable_squares = []
        self.move_units = []
        self.white = white

    def check_move(self, square, capture=False):
        try:
            if board[square[0]][square[1]] is None:
                return True
        except IndexError:
            return False

        if capture:
            return self.check_capture(square)

        return False

    def check_capture(self, square):
        try:
            square_occupant = board[square[0]][square[1]]
        except IndexError:
            return False
        if square_occupant is ChessPiece:
            return self.white ^ square_occupant.white
        return False


# TODO: Implement en passant rule for pawns
class Pawn(ChessPiece):
    def __init__(self, starting_pos, white):
        super().__init__(1, starting_pos, white)
        if self.white:
            self.move_units = [np.array([1, 0])]
        else:
            self.move_units = [np.array([-1, 0])]

    def calc_moves(self):
        self.reachable_squares = []

        move = self.position + self.move_units[0]
        if self.check_move(move):
            self.reachable_squares.append(move)

        start_move = self.position + 2 * self.move_units[0]
        if self.position == self.starting_pos and self.check_move(start_move):
            self.reachable_squares.append(start_move)

        capture1 = move + np.array([0, 1])
        if self.check_capture(capture1):
            self.reachable_squares.append(capture1)

        capture2 = move + np.array([0, -1])
        if self.check_capture(capture2):
            self.reachable_squares.append(capture2)


class Bishop(ChessPiece):
    def __init__(self, starting_pos, white):
        super().__init__(3, starting_pos, white)
        self.move_units = [np.array(vec) for vec in [[1, 1], [1, -1], [-1, 1], [-1, -1]]]

    def calc_moves(self):
        self.reachable_squares = []

        found_limit = np.array([False for _ in range(len(self.move_units))])
        dist = 1

        while not np.all(found_limit):
            for i in range(len(found_limit)):
                if not found_limit[i]:
                    move = self.position + self.move_units[i] * dist
                    if self.check_move(move):
                        self.reachable_squares.append(move)
                    else:
                        if self.check_capture(move):
                            self.reachable_squares.append(move)
                        found_limit[i] = True
            dist += 1


class Knight(ChessPiece):
    def __init__(self, starting_pos, white):
        super().__init__(3, starting_pos, white)

    def calc_moves(self):
        self.reachable_squares = []

        for vec in [[1, 2], [1, -2], [-1, 2], [-1, -2], [2, 1], [2, -1], [-2, 1], [-2, -1]]:
            move = self.position + np.array(vec)
            if self.check_move(move, capture=True):
                self.reachable_squares.append(move)


class Rook(ChessPiece):
    def __init__(self, starting_pos, white):
        super().__init__(5, starting_pos, white)
        self.move_units = [np.array(vec) for vec in [[0, 1], [0, -1], [1, 0], [-1, 0]]]

    def calc_moves(self):
        self.reachable_squares = []

        found_limit = np.array([False for _ in range(len(self.move_units))])
        dist = 1

        while not np.all(found_limit):
            for i in range(len(found_limit)):
                if not found_limit[i]:
                    move = self.position + self.move_units[i] * dist
                    if self.check_move(move):
                        self.reachable_squares.append(move)
                    else:
                        if self.check_capture(move):
                            self.reachable_squares.append(move)
                        found_limit[i] = True
            dist += 1


class Queen(ChessPiece):
    def __init__(self, starting_pos, white):
        super().__init__(9, starting_pos, white)
        self.move_units = [np.array(vec) for vec in
                           [[0, 1], [0, -1], [1, 0], [-1, 0], [1, 1], [1, -1], [-1, 1], [-1, -1]]]

    def calc_moves(self):
        self.reachable_squares = []

        found_limit = np.array([False for _ in range(len(self.move_units))])
        dist = 1

        while not np.all(found_limit):
            for i in range(len(found_limit)):
                if not found_limit[i]:
                    move = self.position + self.move_units[i] * dist
                    if self.check_move(move):
                        self.reachable_squares.append(move)
                    else:
                        if self.check_capture(move):
                            self.reachable_squares.append(move)
                        found_limit[i] = True
            dist += 1


class King(ChessPiece):
    def __init__(self, starting_pos, white):
        super().__init__(np.inf, starting_pos, white)
        self.move_units = [np.array(vec) for vec in
                           [[0, 1], [0, -1], [1, 0], [-1, 0], [1, 1], [1, -1], [-1, 1], [-1, -1]]]

    def calc_moves(self):
        self.reachable_squares = []

        for vec in self.move_units:
            move = self.position + vec
            if self.check_move(move, capture=True):
                self.reachable_squares.append(move)
