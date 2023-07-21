import tensorflow as tf
import numpy as np
import pandas as pd
from collections.abc import Iterator, Generator

class PositionDatabase(Generator):
    def __init__(self, data_file, pos_rep="zun", eval_scale=1.0, ignore_mate=True):
        pos_df = pd.read_csv(data_file)

        self.positions = pos_df["FEN"]
        self.evals = pos_df["Evaluation"]
        self.pos_rep = pos_rep
        self.eval_scale = eval_scale

        self.current_item = 0

    def position_array(self, fen_string):
        board, turn, castle, ep, half_moves, full_moves = fen_string.split(" ")

        if "s" in self.pos_rep: # signed piece vectors (White = 1, Black = -1); else "u" for unsigned
            piece_vectors = np.concatenate(
                [
                    -np.eye(6),
                    np.eye(6),
                    np.zeros((1,6))
                ], axis=0
            ).astype(int)
        elif "z" in self.pos_rep: # zero representation for empty squares, else "e" for empty token
            piece_vectors = np.concatenate(
                [
                    np.eye(12),
                    np.zeros((1, 12))
                ], axis=0
            ).astype(int)
        else:
            piece_vectors = np.eye(13).astype(int)

        piece_numbers = dict(zip(['p', 'n', 'b', 'r', 'q', 'k', 'P', 'N', 'B', 'R', 'Q', 'K'], range(12)))

        game_state = []

        board_state = []
        for row in board.split("/"):
            row_state = []
            for square in row:
                if square in piece_numbers.keys():
                    row_state += [piece_vectors[piece_numbers[square]]]
                else:
                    row_state += [piece_vectors[12]]*int(square)
            assert len(row_state) == 8
            board_state += row_state

        game_state += [np.squeeze(np.concatenate(board_state, axis=0))]
        game_state += [np.array([1] if turn == 'w' else [0])]
        game_state += [
            np.array(
                [
                    "K" in castle,
                    "Q" in castle,
                    "k" in castle,
                    "q" in castle
                ]
            ).astype(int)
        ]

        ep_state = np.zeros(16).astype(int)
        if ep != "-":
            ep_state[int(ep[0] == 'c') * 8 + int(ep[1]) - 1] = 1
        game_state += [ep_state]

        if "f" in self.pos_rep: # fifty move rule in effect; otherwise "n" for no fifty move rule
            game_state += [np.array([int(half_moves)])]

        game_state = np.concatenate(game_state, axis=0).astype(np.float32)

        return game_state

    def __len__(self):
        return len(self.positions)

    def send(self, n):

        if n is None:
            n = self.current_item
        self.current_item = (n+1) % len(self)

        position = tf.convert_to_tensor(self.position_array(self.positions[n]))
        evaluation = tf.convert_to_tensor(np.array(float(self.evals[n].replace("#",""))).astype(np.float32))
        return position, evaluation

    def throw(self, type=None, value=None, traceback=None):
        raise StopIteration

    # def __next__(self):
    #     self.current_item += 1
    #     return self.__getitem__(self.current_item - 1)

    def next(self):
        return self.__next__()

    def __call__(self):

        for n in range(len(self.positions)):
            yield self.send(n)