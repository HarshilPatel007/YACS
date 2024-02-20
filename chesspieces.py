import vars
import chess
from PySide6 import QtCore, QtGui, QtSvg, QtSvgWidgets, QtWidgets

class ChessPieces:

    def __init__(self, chessboard, is_chessboard_flipped, scene, piece_set="staunty"):
        self.chessboard = chessboard
        self.is_chessboard_flipped = is_chessboard_flipped
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

                if self.is_chessboard_flipped:
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
