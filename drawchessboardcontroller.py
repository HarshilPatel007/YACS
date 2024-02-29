#   This file is part of YACS
#
#   YACS free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#   YACS is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License along with YACS. If not, see <https://www.gnu.org/licenses/>. 

import random

import chess
from PySide6 import QtCore, QtGui, QtWidgets

import config
from chesspieces import ChessPieces
from movemanager import MoveManager
from chessboard import ChessBoard
from chessboardevents import ChessBoardEvents



class DrawChessBoard(QtWidgets.QGraphicsView, ChessBoard):
    def __init__(self, game):
        super().__init__()
        self.scene = QtWidgets.QGraphicsScene()
        self.setScene(self.scene)
        self.setRenderHints(
            QtGui.QPainter.Antialiasing | QtGui.QPainter.SmoothPixmapTransform
        )
        # the game on the board
        self.game = game
        self.chess_pieces = ChessPieces(self)
        self.chess_pieces.load_chess_piece_images()
        self.show_labels = True
        self.highlight_manager = ChessBoardHighlightManager(self)
        self.events = ChessBoardEvents(self)
        self.marked_squares = {}

    def draw_squares(self):
        """
        draws squares forming a chessboard
        """
        for square in chess.SQUARES:
            col, row, x, y = self.get_square_coordinates(square)

            rect = self.scene.addRect(x, y, config.SQUARE_SIZE, config.SQUARE_SIZE)

            rect_color = (
                config.THEME_COLORS["light_square"]
                if (row + col) % 2 == 0
                else config.THEME_COLORS["dark_square"]
            )

            rect.setPen(QtCore.Qt.NoPen)
            rect.setBrush(QtGui.QColor(rect_color))

    def draw_labels(self):
        """
        draws rank (1-8) & file (a-h) label
        """
        # Clear existing labels
        for item in self.scene.items():
            if isinstance(item, QtWidgets.QGraphicsTextItem):
                self.scene.removeItem(item)

        for square in chess.SQUARES:
            col, row, x, y = self.get_square_coordinates(square)

            # Determine label position
            row_label_x = x + config.SQUARE_SIZE / 8 - 10
            row_label_y = y + config.SQUARE_SIZE / 8 - 10

            col_label_x = x + config.SQUARE_SIZE - config.SQUARE_SIZE / 15 - 10
            col_label_y = y + config.SQUARE_SIZE - config.SQUARE_SIZE / 8 - 15

            label_color = (
                config.THEME_COLORS["light_square"]
                if (row + col) % 2 != 0
                else config.THEME_COLORS["dark_square"]
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
        self.starting_board_position_fen = (
            self.board.board_fen()
        )  # hack to get the fen of only starting position

    def flip_chessboard(self):
        self.is_board_flipped = not self.is_board_flipped
        if self.show_labels:
            self.draw_labels()

        self.highlight_manager.update_marked_squares_coordinates()
        self.highlight_manager.delete_highlighted_squares(
            config.THEME_COLORS["highlight_square"]
        )
        if len(self.board.move_stack) > 0:
            self.highlight_manager.highlight_source_and_destination_squares()

        self.chess_pieces.redraw_pieces()

    def mousePressEvent(self, event):
        self.events.mousePress(event)


class ChessBoardHighlightManager:
    def __init__(self, board_updater):
        self.board_updater = board_updater
        self.game = board_updater.game
        self.chessboard = self.game.chessboard
        self.move_manager = self.game.move_manager

    def highlight_legal_moves(self, square_number):
        """
        highlights the legal moves of a selected piece/square
        """
        legal_moves = self.game.move_manager.get_legal_moves(square_number)

        for target_square in set(move.to_square for move in legal_moves):
            col, row, x, y = self.chessboard.get_square_coordinates(target_square)

            # Add a circle in the center of the square
            circle = self.board_updater.scene.addEllipse(
                x + config.SQUARE_SIZE / 3,
                y + config.SQUARE_SIZE / 3,
                config.SQUARE_SIZE / 3,
                config.SQUARE_SIZE / 3,
            )
            circle.setPen(QtCore.Qt.NoPen)
            circle.setBrush(QtGui.QColor(config.THEME_COLORS["highlight_legal_moves"]))
            circle.setOpacity(0.45)

    def delete_highlighted_legal_moves(self):
        items = self.board_updater.scene.items()
        for item in items:
            if isinstance(item, QtWidgets.QGraphicsEllipseItem):
                brush_color = item.brush().color()
                if brush_color == QtGui.QColor(
                    config.THEME_COLORS["highlight_legal_moves"]
                ):
                    self.board_updater.scene.removeItem(item)

    def create_highlighted_square(self, square, color, opacity):
        """
        creates the rect at the source and destination squares
        """
        rect = QtWidgets.QGraphicsRectItem()
        rect.setRect(
            square[0] * config.SQUARE_SIZE,
            square[1] * config.SQUARE_SIZE,
            config.SQUARE_SIZE,
            config.SQUARE_SIZE,
        )
        rect.setPen(QtCore.Qt.NoPen)
        rect.setBrush(QtGui.QColor(color))
        rect.setOpacity(opacity)
        return self.board_updater.scene.addItem(rect)

    def delete_highlighted_squares(self, color):
        items = self.board_updater.scene.items()
        for item in items:
            if isinstance(item, QtWidgets.QGraphicsRectItem):
                brush_color = item.brush().color()
                if brush_color == QtGui.QColor(color):
                    self.board_updater.scene.removeItem(item)

    def create_marked_square(self, square_number, color):
        """
        creates the rect at the given pos.
        """
        if square_number in self.board_updater.marked_squares:
            return

        col, row, x, y = self.chessboard.get_square_coordinates(square_number)

        # Check if there is already a rectangle at the given position
        existing_rects = self.chessboard.scene.items(
            QtCore.QRectF(x, y, config.SQUARE_SIZE, config.SQUARE_SIZE)
        )
        for rect in existing_rects:
            if isinstance(rect, QtWidgets.QGraphicsRectItem):
                brush_color = rect.brush().color()
                if brush_color == QtGui.QColor(color):
                    return

        rect = self.chessboard.scene.addRect(
            x, y, config.SQUARE_SIZE, config.SQUARE_SIZE
        )
        rect.setPen(QtCore.Qt.NoPen)
        rect.setBrush(QtGui.QColor(color))
        rect.setOpacity(0.90)
        self.chessboard.marked_squares[square_number] = rect
        self.chessboard.chess_pieces.redraw_pieces()

    def delete_marked_square(self, square):
        if square in self.chessboard.marked_squares:
            rect = self.chessboard.marked_squares[square]
            self.chessboard.scene.removeItem(rect)
            del self.chessboard.marked_squares[square]

    def delete_marked_squares(self):
        for square, rect in self.board_updater.marked_squares.items():
            self.chessboard.scene.removeItem(rect)
        self.board_updater.marked_squares.clear()

    def update_marked_squares_coordinates(self):
        for square, rect in self.board_updater.marked_squares.items():
            col, row, x, y = self.chessboard.get_square_coordinates(square)
            rect.setRect(x, y, config.SQUARE_SIZE, config.SQUARE_SIZE)

    def highlight_source_and_destination_squares(self):
        (
            source_square,
            destination_square,
        ) = self.move_manager.get_source_and_destination_square()
        self.create_highlighted_square(
            source_square, config.THEME_COLORS["highlight_square"], 0.50
        )
        self.create_highlighted_square(
            destination_square, config.THEME_COLORS["highlight_square"], 0.50
        )
