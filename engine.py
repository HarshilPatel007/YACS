import chess.engine


class Engine:

    def __init__(self, chessboard):
        self.chessboard = chessboard
        self.engine = None

    async def get_engine_move(self):
        engine_options = {
            "Skill Level": 15,
            "UCI_Elo": 1500,
        }
        transport, self.engine = await chess.engine.popen_uci(
            "engine/stockfish"
        )
        result = await self.engine.play(
            self.chessboard.board,
            chess.engine.Limit(time=10, depth=10),
            options=engine_options,
        )

        self.chessboard.move_manager.is_piece_moved = True
        await self.engine.quit()
        self.engine = None

        return result.move
