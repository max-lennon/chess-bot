import tkinter as tk
import numpy as np
from PIL import ImageTk, Image
from chess_piece import *
from chess_game import ChessBoard

type_dict = {1: "pawn", 2: "bishop", 3: "knight", 4: "rook", 5: "queen", 6: "king"}

class Application(tk.Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self.master = master

        # Get the width and height of the screen as instance variables
        self.screenwidth = master.winfo_screenwidth()
        self.screenheight = master.winfo_screenheight()

        self.board = ChessBoard()
        self.piece_dict = {}
        self.move_labels = []

        self.pack()
        self.create_widgets()
        self.create_pieces()

    def create_widgets(self):
        self.container_frames()

        self.main_canvas()

    def container_frames(self):
        self.main_board_frame = tk.Frame()
        self.main_board_frame.pack(side="left")

    def main_canvas(self):
        # Values chosen by experimentation - can be changed if necessary
        self.canvas_width = int(self.screenheight / 24) * 16
        self.canvas_height = self.canvas_width

        self.main_img_canvas = tk.Canvas(self.main_board_frame, width=self.canvas_width,
                                         height=self.canvas_height, bg="gray")
        main_img = Image.open("./assets/chessboard.png").resize((self.canvas_height, self.canvas_width))

        # Tkinter image needed to pass to create_image in main canvas
        self.canvas_img = ImageTk.PhotoImage(main_img)
        # Object created upon calling create_image - used when changing main image with itemconfig
        self.main_canvas_img = self.main_img_canvas.create_image(0, 0, anchor="nw", image=self.canvas_img)

        self.main_img_canvas.pack(side="left")


    def create_pieces(self):
        for white in [True, False]:
            if white:
                piece_row = 0
                pawn_row = 1
            else:
                piece_row = 7
                pawn_row = 6

            self.add_piece(Rook(np.array([0, piece_row]), white))
            self.add_piece(Rook(np.array([7, piece_row]), white))
            self.add_piece(Knight(np.array([1, piece_row]), white))
            self.add_piece(Knight(np.array([6, piece_row]), white))
            self.add_piece(Bishop(np.array([2, piece_row]), white))
            self.add_piece(Bishop(np.array([5, piece_row]), white))
            self.add_piece(Queen(np.array([3, piece_row]), white))
            self.add_piece(King(np.array([4, piece_row]), white))
            for i in range(8):
                self.add_piece(Pawn(np.array([i, pawn_row]), white))

    def add_piece(self, piece: ChessPiece):

        filename = "./assets/pieces/"
        if piece.white:
            filename += "white_"
        else:
            filename += "black_"
        filename += type_dict[abs(piece.piece_type)]

        if (piece.position[0] + piece.position[1]) % 2 == 0:
            filename += "_dark.png"
        else:
            filename += "_light.png"
        img = Image.open(filename).resize((int(self.canvas_width / 8), int(self.canvas_height / 8)))
        piece_img = ImageTk.PhotoImage(img)

        self.piece_dict[piece] = tk.Label(self.main_img_canvas, bd=0, image=piece_img)
        self.piece_dict[piece].image = piece_img
        piece_x, piece_y = self.get_coords(piece.starting_pos)
        self.piece_dict[piece].bind("<ButtonPress-1>", lambda event: self.show_moves(piece))
        self.piece_dict[piece].place(x=piece_x, y=piece_y)

        self.board.place(piece)

    def show_moves(self, piece: ChessPiece):
        for board_piece in self.piece_dict.keys():
            self.piece_dict[board_piece].bind("<ButtonPress-1>", lambda event, board_piece=board_piece: self.show_moves(board_piece))
        piece.reachable_squares = self.board.calc_moves(piece, self.board.board_state)
        for label in self.move_labels:
            label.destroy()
        self.move_labels = []
        self.piece_dict[piece].bind("<ButtonPress-1>", lambda event: self.cancel_move(piece))

        for i in range(len(piece.reachable_squares)):
            square = piece.reachable_squares[i]
            if self.board.board[square[0]][square[1]] is None:
                if (square[0] + square [1]) % 2 == 0:
                    dark_img = ImageTk.PhotoImage(Image.open("./assets/highlight_dark.png").resize((int(self.canvas_width / 8), int(self.canvas_height / 8))))
                    self.move_labels.append(tk.Label(self.main_img_canvas, bd=0, image=dark_img))
                    self.move_labels[i].image = dark_img
                else:
                    light_img = ImageTk.PhotoImage(Image.open("./assets/highlight_light.png").resize((int(self.canvas_width / 8), int(self.canvas_height / 8))))
                    self.move_labels.append(tk.Label(self.main_img_canvas, bd=0, image=light_img))
                    self.move_labels[i].image = light_img
                self.move_labels[i].bind("<ButtonPress-1>", lambda event, square=square: self.move_piece(piece, square))
            else:
                target_piece = self.board.board[square[0]][square[1]]
                filename = "./assets/pieces/"
                if target_piece.white:
                    filename += "white_"
                else:
                    filename += "black_"
                filename += type_dict[abs(target_piece.piece_type)]

                if (target_piece.position[0] + target_piece.position[1]) % 2 == 0:
                    filename += "_dark_highlight.png"
                else:
                    filename += "_light_highlight.png"
                img = Image.open(filename).resize((int(self.canvas_width / 8), int(self.canvas_height / 8)))
                highlight_img = ImageTk.PhotoImage(img)
                self.move_labels.append(tk.Label(self.main_img_canvas, bd=0, image=highlight_img))
                self.move_labels[i].image = highlight_img
                self.move_labels[i].bind("<ButtonPress-1>", lambda event, square=square: self.capture_piece(piece, square))
            square_x, square_y = self.get_coords(square)
            self.move_labels[i].place(x=square_x, y=square_y)

    def cancel_move(self, piece: ChessPiece):
        for label in self.move_labels:
            label.destroy()
        self.move_labels = []
        self.piece_dict[piece].bind("<ButtonPress-1>", lambda event: self.show_moves(piece))

    def move_piece(self, piece: ChessPiece, move: np.ndarray):
        self.piece_dict[piece].bind("<ButtonPress-1>", lambda event: self.show_moves(piece))
        prev_pos = piece.position
        if np.asarray(piece.reachable_squares).__contains__(move):
            if piece.__class__ is Pawn and not any(piece.position == move) and \
                 self.board.board_state[move[0]][move[1]] == 0:
                target_piece = self.board.board[move[0]][move[1]-piece.piece_type]
                for label in self.move_labels:
                    label.destroy()
                self.move_labels = []
                if self.board.capture_piece(piece, move):
                    print("Displaying capture...")
                    self.piece_dict[target_piece].destroy()
                    self.piece_dict.pop(target_piece, None)
                    new_x, new_y = self.get_coords(move)
                    self.piece_dict[piece].place(x=new_x, y=new_y)
                    self.update_bg_color(piece)

            elif self.board.move_piece(piece, move):
                if piece.__class__ is King and prev_pos[0] - move[0] > 1:
                    new_x, new_y = self.get_coords(move)
                    self.piece_dict[piece].place(x=new_x, y=new_y)
                    self.update_bg_color(piece)

                    rook_x, rook_y = self.get_coords(move + np.array([1,0]))
                    self.piece_dict[self.board.board[3][move[1]]].place(x=rook_x, y=rook_y)
                    self.update_bg_color(self.board.board[3][move[1]])

                    for label in self.move_labels:
                        label.destroy()
                    self.move_labels = []
                elif piece.__class__ is King and prev_pos[0] - move[0] < -1:
                    new_x, new_y = self.get_coords(move)
                    self.piece_dict[piece].place(x=new_x, y=new_y)
                    self.update_bg_color(piece)

                    rook_x, rook_y = self.get_coords(move - np.array([1, 0]))
                    self.piece_dict[self.board.board[5][move[1]]].place(x=rook_x, y=rook_y)
                    self.update_bg_color(self.board.board[5][move[1]])

                    for label in self.move_labels:
                        label.destroy()
                    self.move_labels = []
                else:
                    new_x, new_y = self.get_coords(move)
                    self.piece_dict[piece].place(x=new_x, y=new_y)
                    self.update_bg_color(piece)
                    for label in self.move_labels:
                        label.destroy()
                    self.move_labels = []


    def capture_piece(self, piece: ChessPiece, move: np.ndarray):
        self.piece_dict[piece].bind("<ButtonPress-1>", lambda event: self.show_moves(piece))
        if np.asarray(piece.reachable_squares).__contains__(move):
            for label in self.move_labels:
                label.destroy()
            self.move_labels = []
            target_piece = self.board.board[move[0]][move[1]]
            if self.board.capture_piece(piece, move):
                print("Displaying capture...")
                self.piece_dict[target_piece].destroy()
                self.piece_dict.pop(target_piece, None)
                new_x, new_y = self.get_coords(move)
                self.piece_dict[piece].place(x=new_x, y=new_y)
                self.update_bg_color(piece)

    def update_bg_color(self, piece: ChessPiece):
        filename = "./assets/pieces/"
        if piece.white:
            filename += "white_"
        else:
            filename += "black_"
        filename += type_dict[abs(piece.piece_type)]

        if (piece.position[0] + piece.position[1]) % 2 == 0:
            filename += "_dark.png"
        else:
            filename += "_light.png"
        img = Image.open(filename).resize((int(self.canvas_width / 8), int(self.canvas_height / 8)))
        piece_img = ImageTk.PhotoImage(img)
        self.piece_dict[piece].configure(image=piece_img)
        self.piece_dict[piece].image = piece_img

    def get_coords(self, position: np.ndarray):
        half_sq = int(self.canvas_width / 16.0)
        return position[0] * half_sq * 2, (7 - position[1]) * half_sq * 2


if __name__ == '__main__':
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()