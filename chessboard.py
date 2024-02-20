import random

import chess
from PySide6 import QtCore, QtGui, QtSvg, QtSvgWidgets, QtWidgets

import vars
from chesspieces import ChessPieces
from movemanager import MoveManager


class ChessBoard:
    def __init__(self):
        self.fischer_random = False
        self.board = chess.Board(chess960=self.fischer_random)
        self.is_board_flipped = False
        self.move_manager = MoveManager(self)

    def set_chess960_board(self):
        self.board.set_chess960_pos(random.randint(1, 959))

    def get_square_coordinates(self, square):
        """
        col, row, x, y = self.get_square_coordinates(square)
        """
        if self.is_board_flipped:
            col = 7 - chess.square_file(square)
            row = chess.square_rank(square)
        else:
            col = chess.square_file(square)
            row = 7 - chess.square_rank(square)
        return col, row, col * vars.SQUARE_SIZE, row * vars.SQUARE_SIZE

    def get_selected_square_number(self, event):
        """
        return the selected square number
        """
        pos = event.position().toPoint()
        mapped_pos = self.mapToScene(pos)
        col = int(mapped_pos.x() / vars.SQUARE_SIZE)
        row = int(mapped_pos.y() / vars.SQUARE_SIZE)
        if self.is_board_flipped:
            return chess.square(7 - col, row)
        return chess.square(col, 7 - row)


class ChessBoardEvents:
    def __init__(self, chessboard):
        self.chessboard = chessboard

    def mousePress(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:
            square_number = self.chessboard.get_selected_square_number(event)

            if self.chessboard.move_manager.selected_square is None:
                self.chessboard.move_manager.selected_square = square_number
            else:
                if square_number == self.chessboard.move_manager.selected_square:
                    self.chessboard.move_manager.selected_square = None
                    return

                self.chessboard.move_manager.move_piece(square_number)
                if self.chessboard.move_manager.is_piece_moved is True:
                    self.chessboard.move_manager.selected_square = None
                    self.chessboard.chess_pieces.delete_pieces()
                    self.chessboard.chess_pieces.draw_pieces()


class DrawChessBoard(QtWidgets.QGraphicsView, ChessBoard):

    def __init__(self):
        super().__init__()
        self.scene = QtWidgets.QGraphicsScene()
        self.setScene(self.scene)
        self.chess_pieces = ChessPieces(
            self, self.is_board_flipped, self.scene, "cardinal"
        )
        self.chess_pieces.load_chess_piece_images()
        self.show_labels = True
        self.events = ChessBoardEvents(self)

    def draw_squares(self):
        """
        draws squares forming a chessboard
        """
        for square in chess.SQUARES:
            col, row, x, y = self.get_square_coordinates(square)

            rect = self.scene.addRect(x, y, vars.SQUARE_SIZE, vars.SQUARE_SIZE)

            rect_color = (
                vars.THEME_COLORS["light_square"]
                if (row + col) % 2 == 0
                else vars.THEME_COLORS["dark_square"]
            )

            rect.setPen(QtCore.Qt.NoPen)
            rect.setBrush(QtGui.QColor(rect_color))

    def draw_labels(self):
        """
        draws rank (1-8) & file (a-h) label
        """
        for square in chess.SQUARES:
            col, row, x, y = self.get_square_coordinates(square)

            # Determine label position
            row_label_x = x + vars.SQUARE_SIZE / 8 - 10
            row_label_y = y + vars.SQUARE_SIZE / 8 - 10

            col_label_x = x + vars.SQUARE_SIZE - vars.SQUARE_SIZE / 15 - 10
            col_label_y = y + vars.SQUARE_SIZE - vars.SQUARE_SIZE / 8 - 15

            label_color = (
                vars.THEME_COLORS["light_square"]
                if (row + col) % 2 != 0
                else vars.THEME_COLORS["dark_square"]
            )

            # Add label for the first set of columns (a-h)
            if row == 7:
                if self.is_board_flipped:
                    label = self.scene.addText(f'{chr(ord("h")-col)}')
                else:
                    label = self.scene.addText(f'{chr(ord("a")+col)}')
                label.setDefaultTextColor(QtGui.QColor(label_color))
                label.setPos(col_label_x, col_label_y)

            # Add label for the first set of rows (1-8)
            if col == 0:
                if self.is_board_flipped:
                    label = self.scene.addText(f"{row+1}")
                else:
                    label = self.scene.addText(f"{8-row}")
                label.setDefaultTextColor(QtGui.QColor(label_color))
                label.setPos(row_label_x, row_label_y)

    def draw_chessboard(self):
        if self.fischer_random:
            self.set_chess960_board()
        self.draw_squares()
        if self.show_labels:
            self.draw_labels()
        self.chess_pieces.draw_pieces()

    def mousePressEvent(self, event):
        self.events.mousePress(event)
