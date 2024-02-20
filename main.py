from chessboard import DrawChessBoard
import sys
from PySide6 import QtWidgets
import vars


class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.__version__ = vars.VERSION
        self.setWindowTitle(f"YACS - Yet Another Chess Software ({self.__version__})")

        self.chess_board = DrawChessBoard()
        self.setCentralWidget(self.chess_board)
        self.chess_board.draw_chessboard()
        self.chess_board.setFixedSize(vars.SQUARE_SIZE * 8.5, vars.SQUARE_SIZE * 8.5)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = ApplicationWindow()
    window.showMaximized()
    sys.exit(app.exec())
