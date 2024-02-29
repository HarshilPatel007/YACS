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

    def get_source_and_destination_square(self):
        """
        returns the coordinates of the source and destination squares
        of the last move made on the board
        source_square, destination_square = get_source_and_destination_square()
        => (4, 6), (4, 4)
        """
        last_move = self.move_manager.get_last_move()
        if self.is_board_flipped:
            source_square = (
                7 - chess.square_file(last_move.from_square),
                chess.square_rank(last_move.from_square),
            )
            destination_square = (
                7 - chess.square_file(last_move.to_square),
                chess.square_rank(last_move.to_square),
            )
        else:
            source_square = chess.square_file(
                last_move.from_square
            ), 7 - chess.square_rank(last_move.from_square)
            destination_square = chess.square_file(
                last_move.to_square
            ), 7 - chess.square_rank(last_move.to_square)
        return source_square, destination_square

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


class ChessBoardEvents:
    def __init__(self, board_updater):
        self.board_updater = board_updater
        self.game = board_updater.game
        self.move_manager = self.game.move_manager
        self.highlight_manager = board_updater.highlight_manager

    def mousePress(self, event):
        square_number = self.board_updater.get_selected_square_number(event)
        row, col, x, y = self.board_updater.get_square_coordinates(square_number)
        p_color, p_name = self.board_updater.get_selected_piece_color_and_name(
            square_number
        )
        player_turn = self.game.get_turn()

        if event.buttons() == QtCore.Qt.LeftButton:
            if (
                self.game.move_manager.selected_square is None
                and (p_color or p_name) is not None
                and p_color == player_turn
            ):
                self.move_manager.selected_square = square_number
                self.highlight_manager.highlight_legal_moves(
                    self.move_manager.selected_square
                )
            else:
                if square_number == self.move_manager.selected_square:
                    self.move_manager.selected_square = None
                    self.highlight_manager.delete_highlighted_legal_moves()
                    return

                self.move_manager.move_piece(square_number)

                if self.move_manager.is_piece_moved:
                    # this if condition is here because, in chess960 variant, user
                    # have to click on a rook to do castling and `piece` variable of
                    # `get_selected_piece_color_and_name` method returns None if user
                    # try to click on a rook to do castling.
                    # (tested on chess960 position number 665, 342 or similar positions)
                    if self.game.fischer_random and (
                        self.move_manager.is_queenside_castling
                        or self.move_maneger.is_kingside_castling
                    ):
                        piece_color = (
                            "b" if self.game.board.turn == chess.WHITE else "w"
                        )
                        piece_name = "R"
                    else:
                        (
                            piece_color,
                            piece_name,
                        ) = self.move_manager.get_selected_piece_color_and_name(
                            square_number
                        )
                    (
                        source_square,
                        destination_square,
                    ) = self.move_manager.get_source_and_destination_square()

                    self.highlight_manager.delete_highlighted_squares(
                        config.THEME_COLORS["highlight_square"]
                    )
                    self.highlight_manager.highlight_source_and_destination_squares()

                    self.board_updater.chess_pieces.delete_piece(source_square)

                    if self.move_manager.is_capture:
                        self.board_updater.chess_pieces.delete_piece(destination_square)
                        self.move_maneger.is_capture = False

                    self.board_updater.chess_pieces.draw_piece(
                        piece_name, piece_color, destination_square
                    )

                    self.move_manager.is_piece_moved = False
                    self.move_manager.selected_square = None
                    self.highlight_manager.delete_highlighted_legal_moves()
                    self.highlight_manager.delete_marked_squares()

                    square_number = None

        if event.button() == QtCore.Qt.RightButton:
            self.highlight_manager.delete_marked_square(square_number)

            modifiers = event.modifiers()
            if modifiers == QtCore.Qt.ControlModifier:
                self.highlight_manager.create_marked_square(
                    square_number,
                    config.THEME_COLORS["marked_square_ctrl"],
                )
            elif modifiers == QtCore.Qt.AltModifier:
                self.highlight_manager.create_marked_square(
                    square_number,
                    config.THEME_COLORS["marked_square_alt"],
                )
            elif modifiers == QtCore.Qt.ShiftModifier:
                self.highlight_manager.create_marked_square(
                    square_number,
                    config.THEME_COLORS["marked_square_shift"],
                )
            else:
                return


class DrawChessBoard(QtWidgets.QGraphicsView, ChessBoard):
    def __init__(self, game):
        super().__init__()
        self.scene = QtWidgets.QGraphicsScene()
        self.setScene(self.scene)
        self.setRenderHints(
            QtGui.QPainter.Antialiasing | QtGui.QPainter.SmoothPixmapTransform
        )
        self.chess_pieces = ChessPieces(self, self.scene)
        self.chess_pieces.load_chess_piece_images()
        self.show_labels = True
        # the game on the board
        self.game = game
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

    def highlight_legal_moves(self, square_number):
        """
        highlights the legal moves of a selected piece/square
        """
        legal_moves = self.board_updater.move_maneger.get_legal_moves(square_number)

        for target_square in set(move.to_square for move in legal_moves):
            col, row, x, y = self.board_updater.get_square_coordinates(target_square)

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
        for square, rect in self.chessboard.marked_squares.items():
            self.chessboard.scene.removeItem(rect)
        self.chessboard.marked_squares.clear()

    def update_marked_squares_coordinates(self):
        for square, rect in self.chessboard.marked_squares.items():
            col, row, x, y = self.chessboard.get_square_coordinates(square)
            rect.setRect(x, y, config.SQUARE_SIZE, config.SQUARE_SIZE)

    def highlight_source_and_destination_squares(self):
        (
            source_square,
            destination_square,
        ) = self.chessboard.get_source_and_destination_square()
        self.create_highlighted_square(
            source_square, config.THEME_COLORS["highlight_square"], 0.50
        )
        self.create_highlighted_square(
            destination_square, config.THEME_COLORS["highlight_square"], 0.50
        )
