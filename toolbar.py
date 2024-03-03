from PySide6 import QtGui, QtWidgets


class Toolbar(QtWidgets.QToolBar):
    def __init__(self, parent=None):
        super().__init__(parent)

        flip_board_action = QtGui.QAction("Flip Board", parent)
        flip_board_action.triggered.connect(parent.chess_board.flip_chessboard)
        self.addAction(flip_board_action)

        undo_last_move_action = QtGui.QAction("Undo Last Move", parent)
        undo_last_move_action.triggered.connect(parent.chess_board.undo_last_move)
        self.addAction(undo_last_move_action)
