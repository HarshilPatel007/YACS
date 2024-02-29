#   This file is part of YACS
#
#   YACS free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#   YACS is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License along with YACS. If not, see <https://www.gnu.org/licenses/>. 
from PySide6 import QtWidgets
import chess


class MoveManager:
    def __init__(self, game):
        self.game = game
        self.chessboard = game.chessboard
        self.selected_square = None
        self.is_piece_moved = False
        self.is_capture = False
        self.is_ep = False
        self.is_castling = False
        self.is_kingside_castling = False
        self.is_queenside_castling = False

    def get_source_and_destination_square(self):
        """
        returns the coordinates of the source and destination squares
        of the last move made on the board
        source_square, destination_square = get_source_and_destination_square()
        => (4, 6), (4, 4)
        """
        last_move = self.get_last_move()
        if self.chessboard.is_board_flipped:
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

    def move_piece(self, target_square):
        if self.selected_square is not None:
            for move in self.game.board.legal_moves:
                if (
                    move.from_square == self.selected_square
                    and move.to_square == target_square
                ):
                    if self._is_pawn_promotion(target_square):
                        self._show_pawn_promotion_dialog(move)
                    if self.game.board.is_capture(move):
                        self.is_capture = True
                    if self.game.board.is_en_passant(move):
                        self.is_ep = True
                    if self.game.board.is_castling(move):
                        self.is_castling = True
                    if self.game.board.is_kingside_castling(move):
                        self.is_kingside_castling = True
                    if self.game.board.is_queenside_castling(move):
                        self.is_queenside_castling = True


                    self.game.make_move(move)
                    self.is_piece_moved = True
                    break

    def _is_pawn_promotion(self, target_square):
        """
        check if the pawn reached at the last rank or not
        """
        return self.game.board.piece_type_at(
            self.selected_square
        ) == chess.PAWN and (
            (
                self.game.board.turn == chess.WHITE
                and chess.square_rank(target_square) == 7
            )
            or (
                self.game.board.turn == chess.BLACK
                and chess.square_rank(target_square) == 0
            )
        )

    def _show_pawn_promotion_dialog(self, move):
        pawn_promotion = PawnPromotion(self.game)
        pawn_promotion.pawn_promotion_dialog(move)

    def get_last_move(self):
        if len(self.game.board.move_stack) > 0:
            return self.game.board.peek()

    def get_legal_moves(self, square):
        moves = []
        for move in self.game.board.legal_moves:
            if move.from_square == square:
                moves.append(move)
        return moves


class PawnPromotion:
    def __init__(self, chessboard):
        self.chessboard = chessboard

    def pawn_promotion_dialog(self, move):
        piece_options = ["Queen", "Rook", "Knight", "Bishop"]

        dialog = QtWidgets.QDialog(self.chessboard)
        dialog.setModal(True)
        dialog.setWindowTitle("Promote Pawn")
        dialog.setFixedWidth(300)

        layout = QtWidgets.QVBoxLayout(dialog)
        dialog.setLayout(layout)

        # Create a button for each piece option
        for piece in piece_options:
            button = QtWidgets.QPushButton(piece)
            button.clicked.connect(
                lambda move=move, piece=piece: self.promote_pawn(dialog, move, piece)
            )
            layout.addWidget(button)

        dialog.exec()

    def promote_pawn(self, dialog, move, piece):
        piece_map = {
            "Queen": chess.QUEEN,
            "Rook": chess.ROOK,
            "Knight": chess.KNIGHT,
            "Bishop": chess.BISHOP,
        }
        move.promotion = piece_map[piece]

        dialog.accept()  # Close the dialog after promoting the pawn
