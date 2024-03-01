import sys

from PySide6 import QtGui, QtWidgets

import config
from chessboard import DrawChessBoard


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
        toolbar = QtWidgets.QToolBar()
        self.addToolBar(toolbar)

        flip_board_action = QtGui.QAction("Flip Board", self)
        flip_board_action.triggered.connect(self.chess_board.flip_chessboard)
        toolbar.addAction(flip_board_action)

        undo_last_move_action = QtGui.QAction("Undo Last Move", self)
        undo_last_move_action.triggered.connect(
            self.chess_board.undo_last_move
        )
        toolbar.addAction(undo_last_move_action)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = ApplicationWindow()
    window.showMaximized()
    sys.exit(app.exec())
