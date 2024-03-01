import chess
import chess.engine
import asyncio
from PySide6 import QtWidgets


class MoveManager:
    def __init__(self, chessboard):
        self.chessboard = chessboard
        self.selected_square = None
        self.is_piece_moved = False
        self.is_capture = False
        self.is_ep = False
        self.is_castling = False
        self.is_kingside_castling = False
        self.is_queenside_castling = False

    def move_piece(self, target_square):
        if self.selected_square is not None:
            for move in self.chessboard.board.legal_moves:
                if (
                    move.from_square == self.selected_square
                    and move.to_square == target_square
                ):
                    if self._is_pawn_promotion(target_square):
                        self._show_pawn_promotion_dialog(move)
                    if self.chessboard.board.is_capture(move):
                        self.is_capture = True
                    if self.chessboard.board.is_en_passant(move):
                        self.is_ep = True
                    if self.chessboard.board.is_castling(move):
                        self.is_castling = True
                    if self.chessboard.board.is_kingside_castling(move):
                        self.is_kingside_castling = True
                    if self.chessboard.board.is_queenside_castling(move):
                        self.is_queenside_castling = True
                    self.chessboard.board.push(move)
                    self.is_piece_moved = True
                    break

    async def engine_move(self):
        engine_options = {
            "Skill Level": 10,
            "UCI_Elo": 1399,
        }
        transport, self.chessboard.engine = await chess.engine.popen_uci(
            "engine/stockfish"
        )
        result = await self.chessboard.engine.play(
            self.chessboard.board,
            chess.engine.Limit(time=10, depth=10),
            options=engine_options,
        )
        self.chessboard.board.push(result.move)
        self.is_piece_moved = True
        await self.chessboard.engine.quit()
        self.chessboard.engine = None

    def _is_pawn_promotion(self, target_square):
        """
        check if the pawn reached at the last rank or not
        """
        return self.chessboard.board.piece_type_at(
            self.selected_square
        ) == chess.PAWN and (
            (
                self.chessboard.board.turn == chess.WHITE
                and chess.square_rank(target_square) == 7
            )
            or (
                self.chessboard.board.turn == chess.BLACK
                and chess.square_rank(target_square) == 0
            )
        )

    def _show_pawn_promotion_dialog(self, move):
        pawn_promotion = PawnPromotion(self.chessboard)
        pawn_promotion.pawn_promotion_dialog(move)

    def get_last_move(self):
        if len(self.chessboard.board.move_stack) > 0:
            return self.chessboard.board.peek()

    def remove_last_move(self):
        if len(self.chessboard.board.move_stack) > 0:
            return self.chessboard.board.pop()

    def get_legal_moves(self, square_number):
        moves = []
        for move in self.chessboard.board.legal_moves:
            if move.from_square == square_number:
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
