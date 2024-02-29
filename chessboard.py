import random

import chess
from PySide6 import QtCore, QtGui, QtWidgets

import config
from chesspieces import ChessPieces
from movemanager import MoveManager


class ChessBoard:
    def __init__(self):
        self.fischer_random = True
        self.board = chess.Board(chess960=self.fischer_random)
        self.is_board_flipped = False
        self.starting_board_position_fen = None

    def set_chess960_board(self):
        self.board.set_chess960_pos(random.randint(1, 959))

    def get_piece_position(self, piece_name, piece_color):
        """
        returns the list of squares coordinates of the given piece name & color
        get_piece_position(chess.ROOK, chess.WHITE) => [(0, 7), (7, 7)]
        """
        squares = []
        for square in self.board.pieces(piece_name, piece_color):
            if self.is_board_flipped:
                squares.append(
                    (7 - chess.square_file(square), chess.square_rank(square))
                )
            else:
                squares.append(
                    (chess.square_file(square), 7 - chess.square_rank(square))
                )

        return squares

    def get_square_coordinates(self, square_number):
        """
        returns the coordinates of given square number
        col, row, x, y = self.get_square_coordinates(20)
        """
        if self.is_board_flipped:
            col = 7 - chess.square_file(square_number)
            row = chess.square_rank(square_number)
        else:
            col = chess.square_file(square_number)
            row = 7 - chess.square_rank(square_number)
        return col, row, col * config.SQUARE_SIZE, row * config.SQUARE_SIZE

    def get_selected_square_number(self, event):
        """
        return the selected square number
        """
        pos = event.position().toPoint()
        mapped_pos = self.mapToScene(pos)
        col = int(mapped_pos.x() / config.SQUARE_SIZE)
        row = int(mapped_pos.y() / config.SQUARE_SIZE)
        if self.is_board_flipped:
            return chess.square(7 - col, row)
        return chess.square(col, 7 - row)

    def get_selected_piece_color_and_name(self, square_number):
        """
        returns the color & name of the piece of given square number
        """
        piece = self.board.piece_at(square_number)
        if piece:
            piece_color = "w" if piece.color == chess.WHITE else "b"
            piece_name = piece.symbol().upper()
            return piece_color, piece_name
        return None, None


