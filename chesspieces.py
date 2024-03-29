import chess
from PySide6 import QtCore, QtGui, QtSvg, QtSvgWidgets, QtWidgets

import vars


class ChessPieces:

    def __init__(self, chessboard, scene, piece_set="staunty"):
        self.chessboard = chessboard
        self.scene = scene
        self.piece_images = {}
        self.piece_set = piece_set

    def load_chess_piece_images(self):
        piece_names = ["P", "N", "B", "R", "Q", "K"]
        for piece_name in piece_names:
            piece_image_paths = {
                "w": f"assets/pieces/{self.piece_set}/w{piece_name}.svg",
                "b": f"assets/pieces/{self.piece_set}/b{piece_name}.svg",
            }
            for piece_color, image_path in piece_image_paths.items():
                renderer = QtSvg.QSvgRenderer(image_path)
                pixmap = QtGui.QPixmap(vars.SQUARE_SIZE - 10, vars.SQUARE_SIZE - 10)
                pixmap.fill(QtCore.Qt.transparent)
                painter = QtGui.QPainter(pixmap)
                renderer.render(painter)
                painter.end()
                self.piece_images[(piece_color, piece_name)] = pixmap

    def draw_pieces(self):
        piece_list = self.chessboard.board.fen().split()[0]
        square = 0
        for char in piece_list:
            if char.isdigit():
                square += int(char)
            elif char != "/":
                piece_name = char.upper()
                piece_color = "w" if char.isupper() else "b"

                if self.chessboard.is_board_flipped:
                    x = (7 - square % 8) * vars.SQUARE_SIZE + 5
                    y = (7 - square // 8) * vars.SQUARE_SIZE + 5
                else:
                    x = (square % 8) * vars.SQUARE_SIZE + 5
                    y = (square // 8) * vars.SQUARE_SIZE + 5

                piece_item = QtWidgets.QGraphicsPixmapItem(
                    self.piece_images[(piece_color, piece_name)]
                )
                piece_item.setPos(x, y)
                self.scene.addItem(piece_item)

                square += 1

    def delete_pieces(self):
        items = self.scene.items()
        for item in items:
            if isinstance(item, QtWidgets.QGraphicsPixmapItem):
                self.scene.removeItem(item)

    def delete_piece(self, square):
        items = self.scene.items()
        x = square[0] * vars.SQUARE_SIZE + 5
        y = square[1] * vars.SQUARE_SIZE + 5
        for item in items:
            if isinstance(
                item, QtWidgets.QGraphicsPixmapItem
            ) and item.pos() == QtCore.QPointF(x, y):
                self.scene.removeItem(item)

    def get_piece_position(self, piece_name, fen):
        rows = fen.split("/")

        piece_positions = []
        for y, row in enumerate(rows):
            x = 0
            for char in row:
                if char in piece_name:
                    if self.chessboard.is_board_flipped:
                        piece_positions.append((7 - x, 7 - y))
                    else:
                        piece_positions.append((x, y))
                if char.isdigit():
                    x += int(char)
                else:
                    x += 1

        return piece_positions

    def draw_piece(self, piece_name, piece_color, destination_square):
        x = destination_square[0] * vars.SQUARE_SIZE + 5
        y = destination_square[1] * vars.SQUARE_SIZE + 5

        piece_item = QtWidgets.QGraphicsPixmapItem(
            self.piece_images[(piece_color, piece_name)]
        )
        piece_item.setPos(x, y)
        self.scene.addItem(piece_item)

        self.handle_special_cases(piece_color, destination_square)

    def handle_special_cases(self, piece_color, destination_square):
        """
        handle special cases such as, castling & en-passant
        for drawing and removing pieces at source & destination square
        """
        white_rooks_positions = self.chessboard.get_pieces_squares(
            chess.ROOK, chess.WHITE
        )
        black_rooks_positions = self.chessboard.get_pieces_squares(
            chess.ROOK, chess.BLACK
        )
        white_king_position = self.chessboard.get_pieces_squares(
            chess.KING, chess.WHITE
        )
        black_king_position = self.chessboard.get_pieces_squares(
            chess.KING, chess.BLACK
        )

        white_rooks_positions_before_castling = self.get_piece_position(
            ["R"], self.chessboard.starting_board_position_fen
        )
        black_rooks_positions_before_castling = self.get_piece_position(
            ["r"], self.chessboard.starting_board_position_fen
        )
        white_king_position_before_castling = self.get_piece_position(
            ["K"], self.chessboard.starting_board_position_fen
        )
        black_king_position_before_castling = self.get_piece_position(
            ["k"], self.chessboard.starting_board_position_fen
        )

        ep_pawn_square = (
            destination_square[0],
            (
                destination_square[1] + 1
                if piece_color == "w"
                else destination_square[1] - 1
            ),
        )

        # check if the move is kingside castling
        if self.chessboard.move_manager.is_kingside_castling == True:
            # delete the rook from old square
            if piece_color == "w":
                self.delete_piece(white_rooks_positions_before_castling[1])
            if piece_color == "b":
                self.delete_piece(black_rooks_positions_before_castling[1])

            # draw the rook to new square
            rook = QtWidgets.QGraphicsPixmapItem(
                self.piece_images[("w" if piece_color == "w" else "b", "R")]
            )
            if piece_color == "w":
                x = white_rooks_positions[1][0] * vars.SQUARE_SIZE + 5
                y = white_rooks_positions[1][1] * vars.SQUARE_SIZE + 5
            if piece_color == "b":
                x = black_rooks_positions[1][0] * vars.SQUARE_SIZE + 5
                y = black_rooks_positions[1][1] * vars.SQUARE_SIZE + 5
            rook.setPos(x, y)
            self.scene.addItem(rook)

            # draw the king to new square
            king = QtWidgets.QGraphicsPixmapItem(
                self.piece_images[("w" if piece_color == "w" else "b", "K")]
            )
            if piece_color == "w":
                x = white_king_position[0][0] * vars.SQUARE_SIZE + 5
                y = white_king_position[0][1] * vars.SQUARE_SIZE + 5
            if piece_color == "b":
                x = black_king_position[0][0] * vars.SQUARE_SIZE + 5
                y = black_king_position[0][1] * vars.SQUARE_SIZE + 5

            if white_king_position == white_king_position_before_castling:
                pass
            elif black_king_position == black_king_position_before_castling:
                pass
            else:
                king.setPos(x, y)
                self.scene.addItem(king)

            self.chessboard.move_manager.is_kingside_castling = False

        # check if the move is queenside castling
        if self.chessboard.move_manager.is_queenside_castling == True:
            # delete the rook from old square
            if piece_color == "w":
                self.delete_piece(white_rooks_positions_before_castling[0])
            if piece_color == "b":
                self.delete_piece(black_rooks_positions_before_castling[0])

            # draw the rook to new square
            rook = QtWidgets.QGraphicsPixmapItem(
                self.piece_images[("w" if piece_color == "w" else "b", "R")]
            )
            if piece_color == "w":
                x = white_rooks_positions[0][0] * vars.SQUARE_SIZE + 5
                y = white_rooks_positions[0][1] * vars.SQUARE_SIZE + 5
            if piece_color == "b":
                x = black_rooks_positions[0][0] * vars.SQUARE_SIZE + 5
                y = black_rooks_positions[0][1] * vars.SQUARE_SIZE + 5
            rook.setPos(x, y)
            self.scene.addItem(rook)

            # draw the king to new square
            king = QtWidgets.QGraphicsPixmapItem(
                self.piece_images[("w" if piece_color == "w" else "b", "K")]
            )
            if piece_color == "w":
                x = white_king_position[0][0] * vars.SQUARE_SIZE + 5
                y = white_king_position[0][1] * vars.SQUARE_SIZE + 5
            if piece_color == "b":
                x = black_king_position[0][0] * vars.SQUARE_SIZE + 5
                y = black_king_position[0][1] * vars.SQUARE_SIZE + 5

            if white_king_position == white_king_position_before_castling:
                pass
            elif black_king_position == black_king_position_before_castling:
                pass
            else:
                king.setPos(x, y)
                self.scene.addItem(king)

            self.chessboard.move_manager.is_queenside_castling = False

        # check if the move is an en-passant capture
        if self.chessboard.move_manager.is_ep:
            # delete opponent's pawn from the scene at the square
            self.delete_piece(ep_pawn_square)
            self.chessboard.move_manager.is_ep = False
