#   This file is part of YACS
#
#   YACS free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#   YACS is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License along with YACS. If not, see <https://www.gnu.org/licenses/>. 

import chess
from PySide6 import QtCore, QtGui, QtWidgets

import config
from chessboard import ChessBoard



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
                        ) = self.game.chessboard.get_selected_piece_color_and_name(
                            square_number
                        )
                    (
                        source_square,
                        destination_square,
                    ) = self.game.move_manager.get_source_and_destination_square()

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

