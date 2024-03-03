import sys

from PySide6 import QtGui, QtWidgets, QtCore

import config
from chessboard import DrawChessBoard
from toolbar import Toolbar


class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.__version__ = config.VERSION
        self.setWindowTitle(f"YACS - Yet Another Chess Software ({self.__version__})")

        self.chess_board = DrawChessBoard()
        self.setCentralWidget(self.chess_board)
        self.chess_board.draw_chessboard()
        self.chess_board.setFixedSize(
            config.SQUARE_SIZE * 8.5, config.SQUARE_SIZE * 8.5
        )

        # Create a toolbar
        self.toolbar = Toolbar(self)
        self.addToolBar(self.toolbar)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = ApplicationWindow()
    window.showMaximized()
    sys.exit(app.exec())
