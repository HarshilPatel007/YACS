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

    def get_pieces_squares(self, piece_name, piece_color):
        """
        returns the list of squares coordinates where the given pieces are.
        get_pieces_squares(chess.ROOK, chess.WHITE) => [(0, 7), (7, 7)]
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

    def get_square_coordinates(self, square):
        """
        returns the coordinates of given square number
        col, row, x, y = self.get_square_coordinates(20)
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

    def get_source_square_from_move(self, move):
        """
        returns a square where piece is moved from
        """
        if self.is_board_flipped:
            return (
                7 - chess.square_file(move.from_square),
                chess.square_rank(move.from_square),
            )
        return chess.square_file(move.from_square), 7 - chess.square_rank(
            move.from_square
        )

    def get_destination_square_from_move(self, move):
        """
        returns a square where piece is moved to
        """
        if self.is_board_flipped:
            return (
                7 - chess.square_file(move.to_square),
                chess.square_rank(move.to_square),
            )
        return chess.square_file(move.to_square), 7 - chess.square_rank(move.to_square)

    def get_selected_piece_color_and_name(self, selected_square):
        """
        returns the color and name of the piece at the selected square
        """
        piece = self.board.piece_at(selected_square)
        if piece:
            piece_color = "w" if piece.color == chess.WHITE else "b"
            piece_name = piece.symbol().upper()
            return piece_color, piece_name
        return None, None

    def get_board_turn(self):
        """
        returns which player's turn to play
        """
        return "w" if self.board.turn == chess.WHITE else "b"

    def highlight_legal_moves(self, scene, square):
        """
        highlights the legal moves of a selected piece
        """
        legal_moves = self.move_manager.get_legal_moves(square)

        for target_square in set(move.to_square for move in legal_moves):
            col, row, x, y = self.get_square_coordinates(target_square)

            # Add a circle in the center of the square
            circle = scene.addEllipse(
                x + vars.SQUARE_SIZE / 3,
                y + vars.SQUARE_SIZE / 3,
                vars.SQUARE_SIZE / 3,
                vars.SQUARE_SIZE / 3,
            )
            circle.setPen(QtCore.Qt.NoPen)
            circle.setBrush(QtGui.QColor(vars.THEME_COLORS["highlight_legal_moves"]))
            circle.setOpacity(0.45)

    def delete_highlighted_legal_moves(self, scene):
        items = scene.items()
        for item in items:
            if isinstance(item, QtWidgets.QGraphicsEllipseItem):
                brush_color = item.brush().color()
                if brush_color == QtGui.QColor(
                    vars.THEME_COLORS["highlight_legal_moves"]
                ):
                    scene.removeItem(item)


class ChessBoardEvents:
    def __init__(self, chessboard):
        self.chessboard = chessboard

    def mousePress(self, event):
        square_number = self.chessboard.get_selected_square_number(event)
        if event.buttons() == QtCore.Qt.LeftButton:
            if self.chessboard.move_manager.selected_square is None:
                self.chessboard.move_manager.selected_square = square_number
                self.chessboard.highlight_legal_moves(
                    self.chessboard.scene, self.chessboard.move_manager.selected_square
                )
            else:
                if square_number == self.chessboard.move_manager.selected_square:
                    self.chessboard.move_manager.selected_square = None
                    self.chessboard.delete_highlighted_legal_moves(
                        self.chessboard.scene
                    )
                    return

                self.chessboard.move_manager.move_piece(square_number)

                if self.chessboard.move_manager.is_piece_moved is True:
                    piece_color, piece_name = (
                        self.chessboard.get_selected_piece_color_and_name(square_number)
                    )
                    last_move = self.chessboard.move_manager.get_last_move()
                    source_square = self.chessboard.get_source_square_from_move(
                        last_move
                    )
                    destination_square = (
                        self.chessboard.get_destination_square_from_move(last_move)
                    )
                    self.chessboard.chess_pieces.delete_piece(source_square)
                    self.chessboard.chess_pieces.draw_piece(
                        piece_name, piece_color, destination_square
                    )
                    self.chessboard.move_manager.is_piece_moved = False
                    self.chessboard.move_manager.selected_square = None
                    self.chessboard.delete_highlighted_legal_moves(
                        self.chessboard.scene
                    )


class DrawChessBoard(QtWidgets.QGraphicsView, ChessBoard):

    def __init__(self):
        super().__init__()
        self.scene = QtWidgets.QGraphicsScene()
        self.setScene(self.scene)
        self.setRenderHints(
            QtGui.QPainter.Antialiasing | QtGui.QPainter.SmoothPixmapTransform
        )
        self.chess_pieces = ChessPieces(self, self.scene, "cardinal")
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
