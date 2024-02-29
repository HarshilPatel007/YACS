#   This file is part of YACS
#
#   YACS free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#   YACS is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License along with YACS. If not, see <https://www.gnu.org/licenses/>. 

from chessboard import ChessBoard
from movemanager import MoveManager

import chess

class Game:
    """a chess game"""
    def __init__(self, board=None):
        # allow creating games with existing boards
        if board:
            self.chessboard = board
            self.board = self.chessboard.board
        else:
            self.chessboard = ChessBoard()
            self.board = self.chessboard.board


        self.move_manager = MoveManager(self)

        self.playing_white = None #TODO: None will work for now
        self.playing_black = None

        self.moves = [] # moves in this game

        self.fischer_random = False

    # you can tell I am still in java mode, lol
    def get_white_player(self) -> str:
        """get the player playing white, or None if no known"""
        return self.playing_white

    def get_black_player(self) -> str:
        """get the black player or None"""
        return self.playing_black

    def make_move(self, move) -> None:
        """make a move in this game, and add it to the moves made"""
        self.chessboard.board.push(move)
        self.moves.append(move)

    def get_turn(self) -> str: 
        """get who's turn it is: 'w' if white eles 'b'"""
        return "w" if self.board.turn == chess.WHITE else "b"


        
