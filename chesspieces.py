#   This file is part of YACS
#
#   YACS free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#   YACS is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License along with YACS. If not, see <https://www.gnu.org/licenses/>. 

import chess
from PySide6 import QtCore, QtGui, QtSvg, QtWidgets

import config


class ChessPieces:
    def __init__(self, board_updater, piece_set="staunty"):
        self.board_updater = board_updater
        self.piece_images = {}
        self.piece_set = piece_set
        self.move_manager = board_updater.game.move_manager

    def load_chess_piece_images(self):
        piece_names = ["P", "N", "B", "R", "Q", "K"]
        for piece_name in piece_names:
            piece_image_paths = {
                "w": f"assets/pieces/{self.piece_set}/w{piece_name}.svg",
                "b": f"assets/pieces/{self.piece_set}/b{piece_name}.svg",
            }
            for piece_color, image_path in piece_image_paths.items():
                renderer = QtSvg.QSvgRenderer(image_path)
                pixmap = QtGui.QPixmap(config.SQUARE_SIZE - 10, config.SQUARE_SIZE - 10)
                pixmap.fill(QtCore.Qt.transparent)
                painter = QtGui.QPainter(pixmap)
                renderer.render(painter)
                painter.end()
                self.piece_images[(piece_color, piece_name)] = pixmap

    def draw_pieces(self):
        piece_list = self.board_updater.board.board_fen()
        square = 0
        for char in piece_list:
            if char.isdigit():
                square += int(char)
            elif char != "/":
                piece_name = char.upper()
                piece_color = "w" if char.isupper() else "b"

                if self.board_updater.is_board_flipped:
                    x = (7 - square % 8) * config.SQUARE_SIZE + 5
                    y = (7 - square // 8) * config.SQUARE_SIZE + 5
                else:
                    x = (square % 8) * config.SQUARE_SIZE + 5
                    y = (square // 8) * config.SQUARE_SIZE + 5

                piece_item = QtWidgets.QGraphicsPixmapItem(
                    self.piece_images[(piece_color, piece_name)]
                )
                piece_item.setPos(x, y)
                self.board_updater.scene.addItem(piece_item)

                square += 1

    def delete_pieces(self):
        items = self.board_updater.scene.items()
        for item in items:
            if isinstance(item, QtWidgets.QGraphicsPixmapItem):
                self.board_updater.scene.removeItem(item)

    def delete_piece(self, square):
        items = self.board_updater.scene.items()
        x = square[0] * config.SQUARE_SIZE + 5
        y = square[1] * config.SQUARE_SIZE + 5
        for item in items:
            if isinstance(
                item, QtWidgets.QGraphicsPixmapItem
            ) and item.pos() == QtCore.QPointF(x, y):
                self.board_updater.scene.removeItem(item)

    def get_piece_position(self, piece_name, board_fen):
        rows = board_fen.split("/")

        piece_positions = []
        for y, row in enumerate(rows):
            x = 0
            for char in row:
                if char in piece_name:
                    if self.board_updater.is_board_flipped:
                        piece_positions.append((7 - x, 7 - y))
                    else:
                        piece_positions.append((x, y))
                if char.isdigit():
                    x += int(char)
                else:
                    x += 1

        return piece_positions

    def draw_piece(self, piece_name, piece_color, destination_square):
        x = destination_square[0] * config.SQUARE_SIZE + 5
        y = destination_square[1] * config.SQUARE_SIZE + 5

        piece_item = QtWidgets.QGraphicsPixmapItem(
            self.piece_images[(piece_color, piece_name)]
        )
        piece_item.setPos(x, y)
        self.board_updater.scene.addItem(piece_item)

        self.handle_special_cases(piece_color, destination_square)

    def handle_special_cases(self, piece_color, destination_square):
        """
        handle special cases such as, castling & en-passant
        for drawing and removing pieces at source & destination square
        """
        white_rooks_positions = self.board_updater.get_piece_position(
            chess.ROOK, chess.WHITE
        )
        black_rooks_positions = self.board_updater.get_piece_position(
            chess.ROOK, chess.BLACK
        )
        white_king_position = self.board_updater.get_piece_position(
            chess.KING, chess.WHITE
        )
        black_king_position = self.board_updater.get_piece_position(
            chess.KING, chess.BLACK
        )

        white_rooks_positions_before_castling = self.get_piece_position(
            ["R"], self.board_updater.starting_board_position_fen
        )
        black_rooks_positions_before_castling = self.get_piece_position(
            ["r"], self.board_updater.starting_board_position_fen
        )

        ep_pawn_square = (
            destination_square[0],
            (
                destination_square[1] + 1
                if piece_color == "w"
                else destination_square[1] - 1
            ),
        )

        # check if the move is castling
        if self.move_manager.is_castling:
            rook = QtWidgets.QGraphicsPixmapItem(
                self.piece_images[("w" if piece_color == "w" else "b", "R")]
            )
            if self.move_manager.is_kingside_castling:
                if piece_color == "w":
                    self.delete_piece(white_rooks_positions_before_castling[1])
                    x = white_rooks_positions[1][0] * config.SQUARE_SIZE + 5
                    y = white_rooks_positions[1][1] * config.SQUARE_SIZE + 5
                if piece_color == "b":
                    self.delete_piece(black_rooks_positions_before_castling[1])
                    x = black_rooks_positions[1][0] * config.SQUARE_SIZE + 5
                    y = black_rooks_positions[1][1] * config.SQUARE_SIZE + 5

            if self.move_manager.is_queenside_castling:
                if piece_color == "w":
                    self.delete_piece(white_rooks_positions_before_castling[0])
                    x = white_rooks_positions[0][0] * config.SQUARE_SIZE + 5
                    y = white_rooks_positions[0][1] * config.SQUARE_SIZE + 5
                if piece_color == "b":
                    self.delete_piece(black_rooks_positions_before_castling[0])
                    x = black_rooks_positions[0][0] * config.SQUARE_SIZE + 5
                    y = black_rooks_positions[0][1] * config.SQUARE_SIZE + 5

            rook.setPos(x, y)
            self.board_updater.scene.addItem(rook)

            king = QtWidgets.QGraphicsPixmapItem(
                self.piece_images[("w" if piece_color == "w" else "b", "K")]
            )
            if (
                self.move_manager.is_kingside_castling
                or self.move_manager.is_queenside_castling
            ):
                if piece_color == "w":
                    x = white_king_position[0][0] * config.SQUARE_SIZE + 5
                    y = white_king_position[0][1] * config.SQUARE_SIZE + 5

                if piece_color == "b":
                    x = black_king_position[0][0] * config.SQUARE_SIZE + 5
                    y = black_king_position[0][1] * config.SQUARE_SIZE + 5

            king.setPos(x, y)
            self.board_updater.scene.addItem(king)

            self.move_manager.is_castling = False
            self.move_manager.is_kingside_castling = False
            self.move_manager.is_queenside_castling = False

        # check if the move is an en-passant capture
        if self.move_manager.is_ep:
            # delete opponent's pawn from the scene at the square
            self.delete_piece(ep_pawn_square)
            self.move_manager.is_ep = False

    def redraw_pieces(self):
        self.delete_pieces()
        self.draw_pieces()
