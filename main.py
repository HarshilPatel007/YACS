#   This file is part of YACS
#
#   YACS free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#   YACS is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License along with YACS. If not, see <https://www.gnu.org/licenses/>. 

import sys

from PySide6 import QtGui, QtWidgets

import config
from drawchessboardcontroller import DrawChessBoard
from game import Game


class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.__version__ = config.VERSION
        self.setWindowTitle(f"YACS - Yet Another Chess Software ({self.__version__})")
        
        # create a starting game
        starting_game = Game()

        self.board_updater = DrawChessBoard(starting_game)

        self.setCentralWidget(self.board_updater)
        self.board_updater.draw_chessboard()
        self.board_updater.setFixedSize(
            config.SQUARE_SIZE * 8.5, config.SQUARE_SIZE * 8.5
        )

        # Create a toolbar
        toolbar = QtWidgets.QToolBar()
        self.addToolBar(toolbar)

        flip_board_action = QtGui.QAction("Flip Board", self)
        flip_board_action.triggered.connect(self.board_updater.flip_chessboard)
        toolbar.addAction(flip_board_action)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = ApplicationWindow()
    window.showMaximized()
    sys.exit(app.exec())
